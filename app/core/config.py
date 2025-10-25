"""
Configuration management using Pydantic Settings
"""
import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., description="Telegram bot token")
    telegram_admin_ids: List[int] = Field(default_factory=list, description="Admin user IDs")
    
    # Database Configuration
    database_url: str = Field(..., description="PostgreSQL database URL")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow connections")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    redis_max_connections: int = Field(default=20, description="Redis max connections")
    
    # Security Configuration
    encryption_key: str = Field(..., description="32-character encryption key for API keys")
    
    # AI Model Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    
    # Custom API Configuration
    enable_custom_apis: bool = Field(default=True, description="Enable custom API configurations")
    custom_api_configs: Optional[str] = Field(default=None, description="JSON string of custom API configurations")
    
    # Rate Limiting
    rate_limit_global: int = Field(default=100, description="Global rate limit per window")
    rate_limit_user: int = Field(default=10, description="Per-user rate limit per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Context Management
    context_max_messages: int = Field(default=20, description="Maximum messages in context")
    context_ttl: int = Field(default=900, description="Context TTL in seconds")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Application
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    
    @validator("telegram_admin_ids", pre=True)
    def parse_admin_ids(cls, v):
        """Parse comma-separated admin IDs"""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v
    
    @validator("encryption_key")
    def validate_encryption_key(cls, v):
        """Validate encryption key format"""
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters")
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError("Database URL must use postgresql+asyncpg:// format")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
