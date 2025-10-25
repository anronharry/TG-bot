#!/usr/bin/env python3
"""
基本命令处理器
包含 start、help、clear 等基础命令
"""
from telegram.ext import ContextTypes
from telegram import Update
from app.core.bot_config import Messages
from app.utils import user_utils
from app.utils.message_utils import schedule_delete
from app.services.chat_service import chat_service
from logger_config import bot_logger


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令"""
    user_info = await user_utils.get_info(update)
    bot_logger.log_user_start(user_info['name'], user_info['username'], user_info['id'])
    sent = await update.message.reply_text(Messages.WELCOME)
    await schedule_delete(context.bot, sent.chat_id, sent.message_id)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /help 命令"""
    sent = await update.message.reply_text(Messages.HELP)
    await schedule_delete(context.bot, sent.chat_id, sent.message_id)


async def clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /clear 命令，清除用户对话历史"""
    user_id = update.effective_user.id
    
    # 清除 Redis 中的对话上下文
    await chat_service.clear_user_context(user_id)
    
    # 清除当前会话ID
    session_id_key = f"current_session:{user_id}"
    from app.core.redis_client import redis_client
    await redis_client.delete(session_id_key)
    
    # 清除数据库中的聊天历史记录
    from app.decorators import db_session_decorator
    
    # 获取数据库会话
    if hasattr(context, 'db_session'):
        # 如果已经有数据库会话，直接使用
        await chat_service.delete_user_chat_history(context.db_session, user_id)
    else:
        # 如果没有数据库会话，需要创建一个
        from app.core.database import get_db_session
        async with get_db_session() as session:
            await chat_service.delete_user_chat_history(session, user_id)
    
    sent = await update.message.reply_text(Messages.HISTORY_CLEARED)
    await schedule_delete(context.bot, sent.chat_id, sent.message_id)
