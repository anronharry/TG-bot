#!/usr/bin/env python3
"""
用户相关工具函数
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.bot_config import BotConfig
from app.services.user_service import user_service


async def get_info(update) -> Dict[str, Any]:
    """获取用户信息"""
    return {
        'id': update.effective_user.id, 
        'name': update.effective_user.first_name or "用户", 
        'username': update.effective_user.username or "无用户名"
    }


async def is_admin(user_id: int) -> bool:
    """检查用户是否为管理员"""
    return user_id in BotConfig.ADMIN_IDS


async def is_group_admin(update) -> bool:
    """检查用户是否为群组管理员"""
    if not hasattr(update, 'effective_user'):
        return False
    
    if await is_admin(update.effective_user.id):
        return True
    
    if update.effective_chat.type in ['group', 'supergroup']:
        try:
            chat_member = await update.get_bot().get_chat_member(
                chat_id=update.effective_chat.id, 
                user_id=update.effective_user.id
            )
            return chat_member.status in ['administrator', 'creator']
        except Exception:
            return False
    
    return False


async def check_banned(session: AsyncSession, user_id: int) -> bool:
    """检查用户是否被封禁"""
    return await user_service.is_user_banned(session, user_id)
