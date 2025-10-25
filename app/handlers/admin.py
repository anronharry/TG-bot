#!/usr/bin/env python3
"""
管理员命令处理器
"""
from telegram.ext import ContextTypes
from telegram import Update
from app.decorators import db_session_decorator
from app.core.bot_config import Messages
from app.utils import user_utils
from app.services.user_service import user_service
from logger_config import bot_logger


async def admin_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /adminhelp 命令"""
    if not await user_utils.is_group_admin(update):
        await update.message.reply_text(Messages.NO_PERMISSION)
        return
    
    sent = await update.message.reply_text(Messages.ADMIN_HELP, parse_mode='Markdown')
    from app.utils.message_utils import schedule_delete
    await schedule_delete(context.bot, sent.chat_id, sent.message_id)


@db_session_decorator
async def ban_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /ban 命令"""
    await handle_moderation_action(update, context, "ban")


@db_session_decorator
async def unban_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /unban 命令"""
    await handle_moderation_action(update, context, "unban")


async def handle_moderation_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """处理管理员操作（封禁/解封）"""
    session = context.db_session
    
    if not await user_utils.is_group_admin(update):
        await update.message.reply_text(Messages.NO_PERMISSION)
        return
    
    target_user_id, target_username = None, "未知用户"
    user_info = await user_utils.get_info(update)
    
    if update.message.reply_to_message:
        target_user_id = update.message.reply_to_message.from_user.id
        target_username = update.message.reply_to_message.from_user.username or target_username
        if action == "ban":
            try:
                chat_member = await update.get_bot().get_chat_member(
                    chat_id=update.effective_chat.id, 
                    user_id=target_user_id
                )
                if chat_member.status in ['administrator', 'creator'] or target_user_id in context.bot_data.get('admin_ids', []):
                    await update.message.reply_text(Messages.CANNOT_BAN_ADMIN)
                    return
            except Exception:
                pass
    elif context.args:
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text(Messages.INVALID_USER_ID)
            return
    else:
        action_text = "封禁" if action == "ban" else "解封"
        await update.message.reply_text(f"⚠ 用法：\n• 引用要{action_text}用户的消息...\n• 或者使用 `.{action} <用户ID>`")
        return
    
    if action == "ban":
        await user_service.ban_user(session, target_user_id)
        bot_logger.log_admin_ban_user(
            user_info['name'], 
            user_info['username'], 
            user_info['id'], 
            target_username, 
            target_user_id
        )
        msg = f"✅ 用户 @{target_username} (ID: {target_user_id}) 已被封禁。"
    else:
        await user_service.unban_user(session, target_user_id)
        bot_logger.log_admin_unban_user(
            user_info['name'], 
            user_info['username'], 
            user_info['id'], 
            target_username, 
            target_user_id
        )
        msg = f"✅ 用户 @{target_username} (ID: {target_user_id}) 已被解封。"
    
    await update.message.reply_text(msg)