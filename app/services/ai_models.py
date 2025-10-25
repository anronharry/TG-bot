"""
AI model service for handling external API calls
"""
import json
from typing import Dict, List, Optional, Any
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schema import AIModel, UserAPIKey
from app.core.config import settings
from app.core.security import security_manager
from app.core.custom_apis import custom_api_config


class AIModelService:
    """Service for AI model interactions"""
    
    def __init__(self):
        self.api_keys = {
            'openai': settings.openai_api_key,
            'anthropic': settings.anthropic_api_key,
            'google': settings.google_api_key,
        }
    
    async def get_user_api_key(self, session: AsyncSession, user_id: int, model_id: int) -> Optional[str]:
        """Get user's custom API key for a model"""
        stmt = select(UserAPIKey).where(
            UserAPIKey.user_id == user_id,
            UserAPIKey.model_id == model_id
        )
        result = await session.execute(stmt)
        user_api_key = result.scalar_one_or_none()
        
        if user_api_key:
            return security_manager.decrypt(user_api_key.encrypted_api_key)
        return None
    
    async def get_model_config(self, session: AsyncSession, model_id: int) -> Optional[AIModel]:
        """Get AI model configuration"""
        stmt = select(AIModel).where(AIModel.id == model_id, AIModel.is_active == True)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_available_models(self, session: AsyncSession) -> List[AIModel]:
        """Get all available AI models"""
        stmt = select(AIModel).where(AIModel.is_active == True)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    async def call_custom_api(self, messages: List[Dict[str, str]], api_config: Dict[str, Any]) -> str:
        """Call custom API (OpenAI compatible)"""
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # 合并自定义headers
        if api_config.get('headers'):
            headers.update(api_config['headers'])
        
        # 构建payload
        payload = {
            "model": api_config['model_name'],
            "messages": messages
        }
        
        # 合并自定义参数
        if api_config.get('parameters'):
            payload.update(api_config['parameters'])
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_config['api_base_url'],
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    # 检查响应内容类型
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' not in content_type:
                        error_text = await response.text()
                        raise Exception(f"API returned non-JSON content (type: {content_type}): {error_text[:200]}")
                    
                    try:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    except Exception as e:
                        error_text = await response.text()
                        raise Exception(f"JSON decode error: {e} - Response: {error_text[:200]}")
                else:
                    error_text = await response.text()
                    raise Exception(f"Custom API error ({api_config['provider']}): {response.status} - {error_text}")
    
    async def call_openai_api(self, messages: List[Dict[str, str]], api_key: str, model_name: str) -> str:
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
    
    async def call_anthropic_api(self, messages: List[Dict[str, str]], api_key: str, model_name: str) -> str:
        """Call Anthropic API"""
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages to Anthropic format
        system_message = ""
        conversation = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": model_name,
            "max_tokens": 2000,
            "messages": conversation
        }
        
        if system_message:
            payload["system"] = system_message
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["content"][0]["text"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_text}")
    
    async def call_google_api(self, messages: List[Dict[str, str]], api_key: str, model_name: str) -> str:
        """Call Google API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert to Google format
        contents = []
        for msg in messages:
            if msg["role"] != "system":
                contents.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": 2000,
                "temperature": 0.7
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Google API error: {response.status} - {error_text}")
    
    async def generate_response(
        self, 
        session: AsyncSession, 
        user_id: int, 
        model_id: int, 
        messages: List[Dict[str, str]]
    ) -> str:
        """Generate AI response using the specified model"""
        
        # 检查是否是个人自定义模型（ID >= 10000）
        if model_id >= 10000:
            custom_model_id = model_id - 10000
            from app.services.user_custom_models import user_custom_model_service
            from app.models.schema import UserCustomModel
            from sqlalchemy import select
            
            # 获取个人自定义模型
            stmt = select(UserCustomModel).where(
                UserCustomModel.id == custom_model_id,
                UserCustomModel.user_id == user_id,
                UserCustomModel.is_active == True
            )
            result = await session.execute(stmt)
            custom_model = result.scalar_one_or_none()
            
            if not custom_model:
                raise ValueError("Personal custom model not found or inactive")
            
            # 使用个人自定义模型
            api_config = {
                'api_base_url': custom_model.api_endpoint,  # 添加缺失的 api_base_url 字段
                'api_endpoint': custom_model.api_endpoint,
                'api_key': custom_model.encrypted_api_key,  # 暂时不加密
                'model_name': custom_model.model_name,
                'headers': {
                    "Authorization": f"Bearer {custom_model.encrypted_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "TelegramBot/1.0"
                }
            }
            return await self.call_custom_api(messages, api_config)
        
        # 处理全局模型
        model = await self.get_model_config(session, model_id)
        if not model:
            raise ValueError("Model not found or inactive")
        
        # 优先：如果数据库里直接配置了 endpoint 与全局加密秘钥，则优先使用
        try:
            db_endpoint = getattr(model, "api_endpoint", None)
            db_encrypted_key = getattr(model, "encrypted_api_key", None)
        except Exception:
            db_endpoint = None
            db_encrypted_key = None

        if db_endpoint and db_encrypted_key:
            api_key_plain = security_manager.decrypt(db_encrypted_key)
            api_config = {
                'name': model.model_name,
                'provider': model.api_provider,
                'model_name': model.model_name,
                'api_base_url': db_endpoint,
                'api_key': api_key_plain,
                'headers': (getattr(model, 'headers', None) or {}),
                'parameters': (getattr(model, 'parameters', None) or {
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    'stream': False
                }),
                'is_active': True
            }
            return await self.call_custom_api(messages, api_config)

        # Check if this is a custom API model
        custom_model = custom_api_config.get_model_by_name(model.model_name)
        if custom_model:
            # Use custom API configuration
            return await self.call_custom_api(messages, custom_model)
        
        # Get API key (user's custom key or default)
        api_key = await self.get_user_api_key(session, user_id, model_id)
        if not api_key:
            api_key = self.api_keys.get(model.api_provider.lower())
            if not api_key:
                raise ValueError(f"No API key available for {model.api_provider}")
        
        # Call appropriate API based on provider
        if model.api_provider.lower() == "openai":
            return await self.call_openai_api(messages, api_key, model.model_name)
        elif model.api_provider.lower() == "anthropic":
            return await self.call_anthropic_api(messages, api_key, model.model_name)
        elif model.api_provider.lower() == "google":
            return await self.call_google_api(messages, api_key, model.model_name)
        else:
            raise ValueError(f"Unsupported API provider: {model.api_provider}")


# Global AI model service instance
ai_model_service = AIModelService()
