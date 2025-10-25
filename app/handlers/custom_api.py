#!/usr/bin/env python3
"""
自定义API配置处理器
使用 ConversationHandler 实现分步输入：API端点 -> API密钥 -> 模型名称 -> 连接验证 -> 自定义名称 -> 保存
"""
import asyncio
import socket
import json
import re
import aiohttp
from urllib.parse import urlparse
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, 
    filters, CallbackQueryHandler
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update as sql_update

from app.core.database import get_db_session
from app.models.schema import UserCustomModel
from app.services.ai_models import ai_model_service
from app.services.user_service import user_service
from app.core.custom_apis import custom_api_config
from app.core.security import security_manager
from app.decorators import db_session_decorator
from logger_config import bot_logger

# 定义会话状态
ENDPOINT, API_KEY, MODEL_NAME, VALIDATING, CUSTOM_NAME = range(5)

# 定义一个空字典，仅用于向后兼容，后续可以完全移除
user_config_states: Dict[int, Dict[str, Any]] = {}


def escape_markdown(text: str) -> str:
    """转义Markdown特殊字符"""
    if not text:
        return text
    # 转义所有Markdown特殊字符
    return re.sub(r'([_*\[\]()~`>#+=|{}.!-])', r'\\\1', str(text))


@db_session_decorator
async def start_custom_api(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """开始自定义API配置流程"""
    user_id = update.effective_user.id
    
    # 初始化用户数据
    context.user_data['custom_api'] = {
        'api_endpoint': None,
        'api_key': None,
        'model_name': None,
        'custom_name': None
    }
    
    # 使用 context.user_data 存储状态信息
    
    await update.message.reply_text(
        "🔧 **自定义API配置向导**\n\n"
        "我将引导你完成自定义API的配置过程：\n\n"
        "**第1步：API端点**\n"
        "请发送你的API端点URL（例如：https://api.example.com/v1/chat/completions）\n\n"
        "💡 提示：确保端点支持OpenAI兼容的chat completions格式\n\n"
        "随时可发送 /cancel 取消配置",
        parse_mode='Markdown'
    )
    
    return ENDPOINT


@db_session_decorator
async def handle_endpoint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """处理API端点输入"""
    user_id = update.effective_user.id
    endpoint = update.message.text.strip()
    
    # 验证URL格式
    if not endpoint.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ **无效的API端点格式**\n\n"
            "请确保URL以 http:// 或 https:// 开头\n"
            "例如：https://api.example.com/v1/chat/completions\n\n"
            "请重新输入：",
            parse_mode='Markdown'
        )
        return ENDPOINT
    
    # 保存端点
    context.user_data['custom_api']['api_endpoint'] = endpoint
    
    # 状态由 ConversationHandler 管理
    
    await update.message.reply_text(
        f"✅ **API端点已设置**\n\n"
        f"端点：`{endpoint}`\n\n"
        "**第2步：API密钥**\n"
        "请发送你的API密钥（例如：sk-xxxxxxxxxxxxxxxx）\n\n"
        "💡 提示：密钥将被加密存储，确保安全",
        parse_mode='Markdown'
    )
    
    return API_KEY


@db_session_decorator
async def handle_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """处理API密钥输入"""
    user_id = update.effective_user.id
    api_key = update.message.text.strip()
    
    # 基本验证
    if len(api_key) < 10:
        await update.message.reply_text(
            "❌ **API密钥太短**\n\n"
            "请确保输入完整的API密钥\n"
            "例如：sk-xxxxxxxxxxxxxxxx\n\n"
            "请重新输入：",
            parse_mode='Markdown'
        )
        return API_KEY
    
    # 保存密钥
    context.user_data['custom_api']['api_key'] = api_key
    
    # 状态由 ConversationHandler 管理
    
    await update.message.reply_text(
        f"✅ **API密钥已设置**\n\n"
        f"密钥：`{api_key[:8]}...`\n\n"
        "**第3步：模型名称**\n"
        "请发送你要使用的模型名称（例如：gpt-4o、claude-3-sonnet）\n\n"
        "💡 提示：这是API调用时使用的实际模型名称",
        parse_mode='Markdown'
    )
    
    return MODEL_NAME


@db_session_decorator
async def handle_model_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """处理模型名称输入"""
    user_id = update.effective_user.id
    model_name = update.message.text.strip()
    
    # 基本验证
    if len(model_name) < 2:
        await update.message.reply_text(
            "❌ **模型名称太短**\n\n"
            "请输入有效的模型名称\n"
            "例如：gpt-4o、claude-3-sonnet\n\n"
            "请重新输入：",
            parse_mode='Markdown'
        )
        return MODEL_NAME
    
    # 保存模型名称
    context.user_data['custom_api']['model_name'] = model_name
    
    # 状态由 ConversationHandler 管理
    
    await update.message.reply_text(
        f"✅ **模型名称已设置**\n\n"
        f"模型：`{model_name}`\n\n"
        "**第4步：连接验证**\n"
        "正在测试API连接...\n\n"
        "⏳ 请稍候...",
        parse_mode='Markdown'
    )
    
    # 开始验证过程
    return await validate_connection(update, context)


@db_session_decorator
async def validate_connection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """验证API连接"""
    user_id = update.effective_user.id
    config = context.user_data['custom_api']
    
    try:
        # 构建测试请求
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TelegramBot/1.0"
        }
        
        payload = {
            "model": config['model_name'],
            "messages": [
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            "max_tokens": 10,
            "temperature": 0.7
        }
        
        # 先测试域名解析
        parsed_url = urlparse(config['api_endpoint'])
        hostname = parsed_url.hostname
        
        try:
            socket.getaddrinfo(hostname, 443)
        except socket.gaierror as e:
            raise Exception(f"域名解析失败: {hostname} - {str(e)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config['api_endpoint'],
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                # 获取响应内容类型
                content_type = response.headers.get('content-type', '')
                
                if response.status == 200:
                    # 检查响应内容类型
                    if 'application/json' not in content_type:
                        error_text = await response.text()
                        raise Exception(f"API返回非JSON内容 (类型: {content_type}): {error_text[:200]}")
                    
                    try:
                        data = await response.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            # 验证成功
                            response_text = data['choices'][0]['message']['content'][:50]
                            # 使用转义函数处理所有内容
                            escaped_endpoint = escape_markdown(config['api_endpoint'])
                            escaped_model = escape_markdown(config['model_name'])
                            escaped_response = escape_markdown(response_text)
                            
                            # 状态由 ConversationHandler 管理
                            
                            await update.message.reply_text(
                                "✅ *API连接验证成功！*\n\n"
                                f"端点：`{escaped_endpoint}`\n"
                                f"模型：`{escaped_model}`\n"
                                f"响应：`{escaped_response}...`\n\n"
                                "*第5步：自定义名称*\n"
                                "请为这个API配置输入一个自定义名称（例如：我的GPT-4、公司Claude）\n\n"
                                "💡 提示：这个名称将显示在模型选择列表中",
                                parse_mode='Markdown'
                            )
                            return CUSTOM_NAME
                        else:
                            raise Exception("API响应格式不正确：缺少choices字段")
                    except json.JSONDecodeError as e:
                        error_text = await response.text()
                        raise Exception(f"JSON解析失败: {str(e)} - 响应: {error_text[:200]}")
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text[:200]}")
                    
    except Exception as e:
        # 验证失败
        # 清除会话数据
        if 'custom_api' in context.user_data:
            del context.user_data['custom_api']
        
        # 状态由 ConversationHandler 管理
        
        await update.message.reply_text(
            f"❌ **API连接验证失败**\n\n"
            f"错误：{str(e)}\n\n"
            "可能的原因：\n"
            "• API端点不正确或无法访问\n"
            "• API密钥无效或过期\n"
            "• 模型名称不支持\n"
            "• 网络连接问题\n"
            "• API服务暂时不可用\n\n"
            "请检查配置后使用 `/customapi` 重新开始",
            parse_mode='Markdown'
        )
        return ConversationHandler.END


@db_session_decorator
async def handle_custom_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """处理自定义名称输入并保存配置"""
    user_id = update.effective_user.id
    custom_name = update.message.text.strip()
    session = context.db_session
    
    # 基本验证
    if len(custom_name) < 2:
        await update.message.reply_text(
            "❌ **自定义名称太短**\n\n"
            "请输入有效的自定义名称\n"
            "例如：我的GPT-4、公司Claude\n\n"
            "请重新输入：",
            parse_mode='Markdown'
        )
        return CUSTOM_NAME
    
    config = context.user_data['custom_api']
    config['custom_name'] = custom_name
    
    # 状态由 ConversationHandler 管理
    
    try:
        # 检查用户是否已有同名的自定义模型
        stmt = select(UserCustomModel).where(
            UserCustomModel.user_id == user_id,
            UserCustomModel.custom_name == custom_name
        )
        result = await session.execute(stmt)
        existing_custom_model = result.scalar_one_or_none()
        
        if existing_custom_model:
            # 更新现有自定义模型
            update_stmt = sql_update(UserCustomModel).where(
                UserCustomModel.id == existing_custom_model.id
            ).values(
                model_name=config['model_name'],
                api_provider=f"自定义-{custom_name}",
                api_endpoint=config['api_endpoint'],
                encrypted_api_key=security_manager.encrypt(config['api_key']),
                is_active=True
            )
            await session.execute(update_stmt)
            custom_model_id = existing_custom_model.id
        else:
            # 创建新的个人自定义模型
            insert_stmt = insert(UserCustomModel).values(
                user_id=user_id,
                custom_name=custom_name,
                model_name=config['model_name'],
                api_provider=f"自定义-{custom_name}",
                api_endpoint=config['api_endpoint'],
                encrypted_api_key=security_manager.encrypt(config['api_key']),
                is_active=True
            )
            result = await session.execute(insert_stmt)
            custom_model_id = result.inserted_primary_key[0]
        
        await session.commit()
        
        # 清除会话数据
        if 'custom_api' in context.user_data:
            del context.user_data['custom_api']
        
        # 状态由 ConversationHandler 管理
        
        # 使用转义函数处理所有用户输入
        escaped_custom_name = escape_markdown(custom_name)
        escaped_endpoint = escape_markdown(config['api_endpoint'])
        escaped_model_name = escape_markdown(config['model_name'])
        
        await update.message.reply_text(
            f"🎉 *自定义API配置完成！*\n\n"
            f"✅ 配置名称：`{escaped_custom_name}`\n"
            f"✅ API端点：`{escaped_endpoint}`\n"
            f"✅ 模型名称：`{escaped_model_name}`\n"
            f"✅ 状态：已激活\n\n"
            "现在你可以使用 /setmodel 命令选择这个自定义模型了！\n\n"
            "💡 提示：你的API密钥已加密保存，安全可靠",
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        # 保存失败
        # 清除会话数据
        if 'custom_api' in context.user_data:
            del context.user_data['custom_api']
        
        # 状态由 ConversationHandler 管理
        
        # 使用转义函数处理错误信息
        escaped_error = escape_markdown(str(e))
        
        await update.message.reply_text(
            f"❌ *保存配置失败*\n\n"
            f"错误：{escaped_error}\n\n"
            "请稍后重试或联系管理员",
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """取消自定义API配置"""
    user_id = update.effective_user.id
    
    # 清除会话数据
    if 'custom_api' in context.user_data:
        del context.user_data['custom_api']
    
    # 向后兼容：清除全局状态字典
    if user_id in user_config_states:
        del user_config_states[user_id]
    
    await update.message.reply_text(
        "❌ **自定义API配置已取消**\n\n"
        "如需重新配置，请使用 `/customapi` 命令",
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END


@db_session_decorator
async def list_custom_apis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /myapis 命令 - 列出用户的自定义API配置"""
    user_id = update.effective_user.id
    session = context.db_session
    
    try:
        # 获取用户的自定义模型
        from app.services.user_custom_models import user_custom_model_service
        custom_models = await user_custom_model_service.get_user_custom_models(session, user_id)
        
        if not custom_models:
            await update.message.reply_text(
                "📝 **你还没有自定义API配置**\n\n"
                "使用 `/customapi` 命令开始配置你的第一个自定义API！",
                parse_mode='Markdown'
            )
            return
        
        # 构建列表消息
        message = "🔧 **你的自定义API配置**\n\n"
        for i, model in enumerate(custom_models, 1):
            message += f"**{i}. {model.custom_name}**\n"
            message += f"   • 模型：`{model.model_name}`\n"
            message += f"   • 端点：`{model.api_endpoint}`\n"
            message += f"   • 状态：{'✅ 激活' if model.is_active else '❌ 停用'}\n\n"
        
        message += "💡 使用 `/setmodel` 选择模型进行对话"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ **获取配置列表失败**\n\n"
            f"错误：{str(e)}",
            parse_mode='Markdown'
        )


@db_session_decorator
async def test_api_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /testapi 命令 - 测试API连接"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "🔧 **API连接测试工具**\n\n"
            "用法：`/testapi <endpoint> <api_key> <model_name>`\n\n"
            "示例：\n"
            "`/testapi https://api.example.com/v1/chat/completions sk-xxx gpt-4o`",
            parse_mode='Markdown'
        )
        return
    
    endpoint = context.args[0]
    api_key = context.args[1]
    model_name = context.args[2]
    
    await update.message.reply_text(
        f"🔍 **正在测试API连接...**\n\n"
        f"端点：`{endpoint}`\n"
        f"模型：`{model_name}`\n"
        f"密钥：`{api_key[:8]}...`\n\n"
        "⏳ 请稍候...",
        parse_mode='Markdown'
    )
    
    # 创建临时配置进行测试
    if 'custom_api' not in context.user_data:
        context.user_data['custom_api'] = {}
    
    context.user_data['custom_api'] = {
        'api_endpoint': endpoint,
        'api_key': api_key,
        'model_name': model_name
    }
    
    # 使用验证函数测试连接
    await validate_connection(update, context)


# 创建 ConversationHandler
custom_api_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("customapi", start_custom_api)],
    states={
        ENDPOINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_endpoint)],
        API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_key)],
        MODEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_model_name)],
        CUSTOM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_name)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="custom_api_conversation",
    persistent=False,  # 后续可以改为 True 并配置持久化
)