#!/usr/bin/env python3
"""
消息处理工具函数
"""
import asyncio
from app.core.bot_config import BotConfig
from logger_config import bot_logger


async def schedule_delete(bot, chat_id: int, message_id: int, delay: int = BotConfig.DELETE_DELAY):
    """计划删除消息"""
    async def _delete():
        try:
            await asyncio.sleep(delay)
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            bot_logger.log_delete_message_error(str(e))
    
    asyncio.create_task(_delete())


async def safe_send(bot, chat_id, text, max_retries=BotConfig.MAX_RETRIES, **kwargs):
    """安全发送消息，带重试机制"""
    for attempt in range(max_retries):
        try:
            return await asyncio.wait_for(
                bot.send_message(chat_id=chat_id, text=text, **kwargs), 
                timeout=BotConfig.TIMEOUT
            )
        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                bot_logger.warning(f"发送消息超时，重试 {attempt + 1}/{max_retries}")
                await asyncio.sleep(1)
            else:
                bot_logger.error("发送消息失败，已达到最大重试次数")
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                bot_logger.warning(f"发送消息错误，重试 {attempt + 1}/{max_retries}: {e}")
                await asyncio.sleep(1)
            else:
                raise
