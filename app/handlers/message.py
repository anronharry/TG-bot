#!/usr/bin/env python3
"""
消息处理器
处理用户发送的普通消息，调用AI生成回复
"""
import asyncio
import uuid
from telegram.ext import ContextTypes
from telegram import Update
from app.decorators import db_session_decorator
from app.core.bot_config import Messages, BotConfig
from app.utils import user_utils, model_utils
from app.utils.message_utils import safe_send
from app.services.user_service import user_service
from app.services.ai_models import ai_model_service
from app.services.chat_service import chat_service
from app.core.redis_client import redis_client
from app.core.config import settings
from logger_config import bot_logger


async def safely_delete_message(bot, chat_id: int, message_id: int) -> None:
    """安全地删除消息，忽略任何错误"""
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        bot_logger.log_delete_message_error(str(e))


@db_session_decorator
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理用户发送的普通消息"""
    # 从 context 获取会话
    session = context.db_session
    
    # 获取用户信息
    user_id = update.effective_user.id
    user_message = update.message.text
    user_info = await user_utils.get_info(update)
    chat_type = update.effective_chat.type
    chat_title = getattr(update.effective_chat, 'title', '私聊')
    
    # 记录用户消息
    bot_logger.log_user_message(
        user_info['name'], 
        user_info['username'], 
        user_info['id'], 
        chat_title, 
        chat_type, 
        user_message
    )
    
    # 自定义API流程已迁移到 ConversationHandler，不再需要检查全局状态
    
    # 获取或创建用户
    await user_service.get_or_create_user(
        session, 
        user_id=user_id, 
        username=user_info['username'], 
        first_name=user_info['name']
    )
    
    # 检查用户是否被封禁
    if await user_utils.check_banned(session, user_id):
        bot_logger.log_user_banned_attempt(
            user_info['name'], 
            user_info['username'], 
            user_id
        )
        await update.message.reply_text(Messages.USER_BANNED, parse_mode='Markdown')
        return
    
    # 检查是否是模型选择消息
    model_type, model = await model_utils.find_selected_model(session, user_id, user_message)
    if model_type:
        model_id = model.id if model_type == 'global' else 10000 + model.id
        await user_service.set_user_model(session, user_id, model_id)
        model_name = f"{model.model_name} ({model.api_provider})" if model_type == 'global' else f"{model.custom_name} ({model.model_name})"
        bot_logger.log_model_selection(
            user_info['name'], 
            user_info['username'], 
            user_info['id'], 
            model_name, 
            model_type
        )
        await update.message.reply_text(f"✅ 已选择模型：{model_name}")
        return
    
    # 检查用户是否已选择模型
    selected_model_id = await user_service.get_user_model(session, user_id)
    if not selected_model_id:
        await update.message.reply_text(Messages.SELECT_MODEL_FIRST, parse_mode='Markdown')
        return
    
    # 显示"正在输入"状态
    try:
        await asyncio.wait_for(
            context.bot.send_chat_action(
                chat_id=update.effective_chat.id, 
                action="typing"
            ), 
            timeout=10.0
        )
    except Exception as e:
        bot_logger.log_typing_error(str(e))
    
    # 发送处理中提示
    processing_msg = None
    try:
        processing_msg = await safe_send(
            context.bot, 
            update.effective_chat.id, 
            Messages.PROCESSING
        )
    except Exception as e:
        bot_logger.log_processing_message_error(str(e))
    
    # 调用AI生成回复
    try:
        bot_logger.log_ai_processing_start(
            user_info['name'], 
            user_info['username'], 
            user_info['id'], 
            str(selected_model_id), 
            len(user_message)
        )
        
        # 获取历史对话记录
        history_messages = await chat_service.get_user_recent_history(session, user_id)
        
        # 传递用户ID到AI系统，但不记录日志
        
        # 准备消息，包含历史记录和用户ID
        messages = await chat_service.format_context_for_ai(history_messages, BotConfig.SYSTEM_PROMPT, user_id)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用AI服务
        ai_response = await ai_model_service.generate_response(
            session, 
            user_id, 
            selected_model_id, 
            messages
        )
        
        # 保存聊天记录
        try:
            # 检查是否有会话上下文键
            session_id_key = f"current_session:{user_id}"
            session_id_str = await redis_client.get(session_id_key)
            
            # 如果没有当前会话或会话已过期，创建新会话
            if not session_id_str:
                session_id = await chat_service.create_new_session()
                await redis_client.set(session_id_key, str(session_id))
                await redis_client.expire(session_id_key, settings.context_ttl)  # 设置相同的过期时间
            else:
                # 使用现有会话
                session_id = uuid.UUID(session_id_str)
            
            # 保存到相同会话ID
            await chat_service.save_chat_history(
                session, 
                session_id=session_id, 
                user_id=user_id, 
                group_id=None, 
                messages=[
                    {"role": "user", "content": user_message}, 
                    {"role": "assistant", "content": ai_response}
                ]
            )
        except Exception as e:
            bot_logger.warning(f"保存聊天记录失败: {e}")
        
        # 记录AI响应
        bot_logger.log_ai_response_complete(
            user_info['name'], 
            user_info['username'], 
            user_info['id'], 
            len(ai_response), 
            ai_response
        )
        
        # 删除处理中提示
        if processing_msg:
            await safely_delete_message(context.bot, update.effective_chat.id, processing_msg.message_id)
        
        # 发送AI回复
        await safe_send(context.bot, update.effective_chat.id, ai_response)
        
    except Exception as e:
        # 处理错误
        bot_logger.log_ai_processing_error(
            user_info['name'], 
            user_info['username'], 
            user_info['id'], 
            str(e)
        )
        
        # 删除处理中提示
        if processing_msg:
            await safely_delete_message(context.bot, update.effective_chat.id, processing_msg.message_id)
        
        # 发送错误提示
        await update.message.reply_text(Messages.AI_ERROR, parse_mode='Markdown')