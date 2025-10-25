#!/usr/bin/env python3
"""
自定义装饰器模块
"""
from functools import wraps
from app.core.database import get_db_session

def db_session_decorator(func):
    """
    一个装饰器，用于为Telegram Bot的handler提供数据库会话。
    它会自动创建会话，并将其通过 context.db_session 传递给handler，
    然后在handler执行完毕后自动关闭会话。
    """
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        # 使用 async with 来确保会话在结束后被正确关闭
        async with get_db_session() as session:
            # 将 session 对象注入到 context 中，以便后续的函数可以访问
            context.db_session = session
            # 执行原始的 handler 函数
            return await func(update, context, *args, **kwargs)
    return wrapper