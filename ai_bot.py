#!/usr/bin/env python3
"""
AI对话机器人版本，支持真正的AI对话功能 - 优化精简版 (模块化重构后)
"""
import traceback
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

# ==================== 导入配置 ====================
from app.core.bot_config import BotConfig
from logger_config import bot_logger

# ==================== 导入处理器 ====================
# 基本命令处理器
from app.handlers.common import start_handler, help_handler, clear_handler

# 管理员命令处理器
from app.handlers.admin import admin_help_handler, ban_user_handler, unban_user_handler

# 模型相关处理器
from app.handlers.model import setmodel_handler

# 自定义API处理器
from app.handlers.custom_api import (
    custom_api_conv_handler,
    list_custom_apis_handler,
    test_api_handler
)

# 消息处理器
from app.handlers.message import message_handler

# 用户相关处理器
from app.handlers.user import setkey_handler

# 装饰器
from app.decorators import db_session_decorator


# ==================== 主函数 ====================
def main():
    """主函数"""
    logger = bot_logger.logger
    bot_logger.log_bot_start(BotConfig.BOT_TOKEN[:10])
    
    try:
        # 配置请求参数
        request = HTTPXRequest(
            connection_pool_size=8, 
            read_timeout=30, 
            write_timeout=30, 
            connect_timeout=30, 
            pool_timeout=30
        )
        
        # 创建应用
        application = Application.builder().token(BotConfig.BOT_TOKEN).request(request).build()
        
        # ==================== 添加处理器 ====================
        # 基本命令处理器
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("help", help_handler))
        application.add_handler(CommandHandler("clear", clear_handler))
        application.add_handler(CommandHandler("adminhelp", admin_help_handler))
        
        # 模型相关命令处理器
        application.add_handler(CommandHandler("setmodel", setmodel_handler))
        application.add_handler(CommandHandler("setkey", db_session_decorator(setkey_handler)))
        
        # 自定义API命令处理器
        application.add_handler(custom_api_conv_handler)
        application.add_handler(CommandHandler("myapis", db_session_decorator(list_custom_apis_handler)))
        application.add_handler(CommandHandler("testapi", db_session_decorator(test_api_handler)))
        
        # 管理员命令处理器
        application.add_handler(CommandHandler("ban", ban_user_handler))
        application.add_handler(CommandHandler("unban", unban_user_handler))
        
        # 管理员正则命令处理器
        application.add_handler(MessageHandler(filters.Regex(r'^\.ban$') & filters.REPLY, ban_user_handler))
        application.add_handler(MessageHandler(filters.Regex(r'^\.unban$') & filters.REPLY, unban_user_handler))
        application.add_handler(MessageHandler(filters.Regex(r'^\.ban\s+\d+$'), ban_user_handler))
        application.add_handler(MessageHandler(filters.Regex(r'^\.unban\s+\d+$'), unban_user_handler))
        
        # AI消息处理器（必须放在最后，因为它处理所有非命令文本）
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # 日志记录
        bot_logger.log_bot_created(BotConfig.BOT_TOKEN[:10])
        bot_logger.log_bot_polling_start()
        
        # 启动轮询
        application.run_polling(drop_pending_updates=True, allowed_updates=['message', 'callback_query'])
        
    except Exception as e:
        bot_logger.error(f"Error: {e}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()