#!/usr/bin/env python3
"""
模型相关命令处理器
包含设置模型、管理模型等功能
"""
from telegram.ext import ContextTypes
from telegram import Update
from app.decorators import db_session_decorator
from app.utils import model_utils
from app.utils.message_utils import schedule_delete
from logger_config import bot_logger


@db_session_decorator
async def setmodel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /setmodel 命令，让用户选择AI模型"""
    session = context.db_session
    user_id = update.effective_user.id
    
    # 构建模型选择键盘
    reply_markup = await model_utils.build_model_keyboard(session, user_id)
    
    # 获取当前选择的模型
    current_model = await model_utils.get_current_model_name(session, user_id)
    
    # 发送选择提示
    sent = await update.message.reply_text(
        f"🤖 选择AI模型\n\n当前选择：{current_model}\n\n请点击下方按钮选择你喜欢的AI模型：", 
        reply_markup=reply_markup
    )
    
    # 设置消息自动删除
    await schedule_delete(context.bot, sent.chat_id, sent.message_id)
