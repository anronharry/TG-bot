#!/usr/bin/env python3
"""
模型相关工具函数
"""
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai_models import ai_model_service
from app.services.user_service import user_service
from app.services.user_custom_models import user_custom_model_service


async def find_selected_model(session: AsyncSession, user_id: int, user_message: str) -> Tuple[Optional[str], Any]:
    """查找用户选择的模型"""
    models = await ai_model_service.get_available_models(session)
    for m in models:
        if user_message == f"{m.model_name} ({m.api_provider})":
            return ('global', m)
    
    custom_models = await user_custom_model_service.get_user_custom_models(session, user_id)
    for m in custom_models:
        if user_message == f"🔧 {m.custom_name} ({m.model_name})":
            return ('custom', m)
    
    return (None, None)


async def build_model_keyboard(session: AsyncSession, user_id: int) -> Dict[str, Any]:
    """构建模型选择键盘"""
    global_models = await ai_model_service.get_available_models(session)
    custom_models = await user_custom_model_service.get_user_custom_models(session, user_id)
    
    keyboard = []
    for m in global_models:
        keyboard.append([f"{m.model_name} ({m.api_provider})"])
    
    if custom_models:
        keyboard.append(["--- 我的自定义模型 ---"])
        for m in custom_models:
            keyboard.append([f"🔧 {m.custom_name} ({m.model_name})"])
    
    return {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}


async def get_current_model_name(session: AsyncSession, user_id: int) -> str:
    """获取当前选择的模型名称"""
    model_id = await user_service.get_user_model(session, user_id)
    if not model_id:
        return '未选择'
    
    models = await ai_model_service.get_available_models(session)
    for m in models:
        if m.id == model_id:
            return f"{m.model_name} ({m.api_provider})"
    
    custom_models = await user_custom_model_service.get_user_custom_models(session, user_id)
    for m in custom_models:
        if m.id == model_id:
            return f"🔧 {m.custom_name} ({m.model_name})"
    
    return '未知模型'
