#!/usr/bin/env python3
"""
日志配置模块
提供统一的日志记录功能，支持不同级别的日志输出
"""
import logging
import os
from datetime import datetime
from typing import Optional


class BotLogger:
    """机器人专用日志记录器"""
    
    def __init__(self, name: str = "ai_bot", log_level: int = logging.INFO):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            'bot.log', 
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 错误日志文件处理器
        error_handler = logging.FileHandler(
            'bot_error.log', 
            encoding='utf-8',
            mode='a'
        )
        error_handler.setLevel(logging.ERROR)
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    # 业务日志方法
    def log_user_message(self, user_name: str, username: str, user_id: int, 
                        chat_title: str, chat_type: str, message: str):
        """记录用户消息"""
        message_preview = message[:100] + ('...' if len(message) > 100 else '')
        self.info(f"📨 收到消息 - 用户: {user_name} (@{username}, ID: {user_id}) | 聊天: {chat_title} ({chat_type}) | 消息: {message_preview}")
    
    def log_user_start(self, user_name: str, username: str, user_id: int):
        """记录用户启动机器人"""
        self.info(f"🚀 用户启动机器人 - 用户: {user_name} (@{username}, ID: {user_id})")
    
    def log_user_banned_attempt(self, user_name: str, username: str, user_id: int):
        """记录被封禁用户尝试使用机器人"""
        self.warning(f"🚫 被封禁用户尝试使用机器人 - 用户: {user_name} (@{username}, ID: {user_id})")
    
    def log_model_selection(self, user_name: str, username: str, user_id: int, 
                           model_name: str, provider: str):
        """记录用户选择模型"""
        self.info(f"🤖 用户选择模型 - 用户: {user_name} (@{username}, ID: {user_id}) | 模型: {model_name} ({provider})")
    
    def log_clear_history(self, user_name: str, username: str, user_id: int, has_history: bool = True):
        """记录用户清除对话历史"""
        status = "清除对话历史" if has_history else "尝试清除对话历史（无历史记录）"
        self.info(f"🗑️ 用户{status} - 用户: {user_name} (@{username}, ID: {user_id})")
    
    def log_ai_processing_start(self, user_name: str, username: str, user_id: int, 
                               model_name: str, message_length: int):
        """记录AI处理开始"""
        self.info(f"🧠 开始AI处理 - 用户: {user_name} (@{username}, ID: {user_id}) | 模型: {model_name} | 消息长度: {message_length}")
    
    def log_ai_response_complete(self, user_name: str, username: str, user_id: int, 
                                response_length: int, response_preview: str):
        """记录AI回复完成"""
        preview = response_preview[:50] + ('...' if len(response_preview) > 50 else '')
        self.info(f"✨ AI回复完成 - 用户: {user_name} (@{username}, ID: {user_id}) | 回复长度: {response_length} | 回复预览: {preview}")
    
    def log_ai_processing_error(self, user_name: str, username: str, user_id: int, error: str):
        """记录AI处理失败"""
        self.error(f"❌ AI处理失败 - 用户: {user_name} (@{username}, ID: {user_id}) | 错误: {error}")
    
    def log_typing_timeout(self, user_id: int):
        """记录发送typing状态超时"""
        self.warning(f"发送typing状态超时，用户ID: {user_id}")
    
    def log_typing_error(self, error: str):
        """记录发送typing状态失败"""
        self.warning(f"发送typing状态失败: {error}")
    
    def log_processing_message_error(self, error: str):
        """记录发送处理中消息失败"""
        self.warning(f"发送处理中消息失败: {error}")
    
    def log_delete_message_error(self, error: str):
        """记录删除处理中消息失败"""
        self.warning(f"删除处理中消息失败: {error}")
    
    # 管理员操作日志
    def log_admin_ban_user(self, admin_name: str, admin_username: str, admin_id: int, 
                          target_username: str, target_user_id: int):
        """记录管理员封禁用户"""
        self.warning(f"🚫 管理员封禁用户 - 操作者: {admin_name} (@{admin_username}, ID: {admin_id}) | 被封禁用户: @{target_username} (ID: {target_user_id})")
    
    def log_admin_ban_user_by_id(self, admin_name: str, admin_username: str, admin_id: int, target_user_id: int):
        """记录管理员通过ID封禁用户"""
        self.warning(f"🚫 管理员通过ID封禁用户 - 操作者: {admin_name} (@{admin_username}, ID: {admin_id}) | 被封禁用户ID: {target_user_id}")
    
    def log_admin_ban_invalid_id(self, admin_name: str, admin_username: str, admin_id: int, invalid_id: str):
        """记录管理员尝试封禁无效用户ID"""
        self.warning(f"❌ 管理员尝试封禁无效用户ID - 操作者: {admin_name} (@{admin_username}, ID: {admin_id}) | 无效ID: {invalid_id}")
    
    def log_admin_unban_user(self, admin_name: str, admin_username: str, admin_id: int, 
                            target_username: str, target_user_id: int):
        """记录管理员解封用户"""
        self.info(f"✅ 管理员解封用户 - 操作者: {admin_name} (@{admin_username}, ID: {admin_id}) | 被解封用户: @{target_username} (ID: {target_user_id})")
    
    def log_admin_unban_user_by_id(self, admin_name: str, admin_username: str, admin_id: int, target_user_id: int):
        """记录管理员通过ID解封用户"""
        self.info(f"✅ 管理员通过ID解封用户 - 操作者: {admin_name} (@{admin_username}, ID: {admin_id}) | 被解封用户ID: {target_user_id}")
    
    def log_admin_unban_invalid_id(self, admin_name: str, admin_username: str, admin_id: int, invalid_id: str):
        """记录管理员尝试解封无效用户ID"""
        self.warning(f"❌ 管理员尝试解封无效用户ID - 操作者: {admin_name} (@{admin_username}, ID: {admin_id}) | 无效ID: {invalid_id}")
    
    # 系统日志
    def log_bot_start(self, bot_token_preview: str):
        """记录机器人启动"""
        self.info(f"🤖 机器人启动 - Token: {bot_token_preview}...")
    
    def log_bot_created(self, bot_token_preview: str):
        """记录机器人创建成功"""
        self.info(f"✅ 机器人创建成功 - Token: {bot_token_preview}...")
    
    def log_bot_polling_start(self):
        """记录机器人开始轮询"""
        self.info("🔄 机器人开始轮询...")
    
    def log_bot_error(self, error: str):
        """记录机器人运行错误"""
        self.error(f"❌ 机器人运行错误: {error}")
    
    def log_data_loaded(self, user_count: int, banned_count: int):
        """记录数据加载"""
        self.info(f"📊 已加载用户数据：{user_count}个用户模型，{banned_count}个被封禁用户")
    
    def log_data_save_error(self, error: str):
        """记录数据保存失败"""
        self.error(f"💾 保存用户数据失败: {error}")
    
    def log_data_load_error(self, error: str):
        """记录数据加载失败"""
        self.error(f"📂 加载用户数据失败: {error}")


# 创建全局日志记录器实例
bot_logger = BotLogger()

# 为了向后兼容，提供简化的接口
def get_logger():
    """获取日志记录器实例"""
    return bot_logger
