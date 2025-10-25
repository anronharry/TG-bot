"""
Custom API configurations for AI models
"""
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings


# 预配置的模型列表（启动时会写入到全局可用模型中，不会清空 api_key）
PRECONFIGURED_MODELS = [
    {
        'name': 'gpt-4.1-nano',
        'provider': 'tbai',
        'model_name': 'gpt-4.1-nano',
        'api_base_url': 'https://tbai.xin/v1/chat/completions',
        'api_key': 'sk-ZzLU9VARB7Nt5rjAT3kM1SShtTJrRX2hv7DvvFXBd2Fpp0WM',
        'headers': {
            'Accept': 'application/json',
            'User-Agent': 'TelegramBot/1.0'
        },
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 2000,
            'stream': False
        },
        'is_active': True
    },
    {
        'name': 'GPT-5o',
        'provider': '200刀',
        'model_name': 'GPT-5o',
        'api_base_url': 'https://api.nyxar.org/v1/chat/completions',
        'api_key': 'sk-oQRDq6dVJbT2jQLT9gyj18f7h4PeviMjEjJDvreq8ekaHLDx',
        'headers': {},
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 2000,
            'stream': False
        },
        'is_active': True
    },
    {
        'name': 'gpt-4o-mini',
        'provider': '红石',
        'model_name': 'gpt-4o-mini',
        # 回退到可解析的 hf.space 域名（完整OpenAI兼容路径）
        'api_base_url': 'https://hongshi1024-l-api.hf.space/v1/chat/completions',
        'api_key': 'sk-PgTINxfx8WQIVftD2uxZFHhydNWeiKEPS2V1QRWSOpV3wiZV',
        # 补充常见所需头部，提升兼容性
        'headers': {
            'Accept': 'application/json',
            'User-Agent': 'TelegramBot/1.0 (+https://example.com)'
        },
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 2000,
            'stream': False
        },
        'is_active': True
    },
]

# 可选：供应商说明（仅用于展示）
PROVIDER_DESCRIPTIONS = {
    'openai': 'OpenAI 兼容 API（包括官方OpenAI、第三方代理等）',
    'claude': 'Anthropic Claude API',
    'gemini': 'Google Gemini API',
    'custom': '自定义 API 接口',
    '200刀': '200刀 服务',
    '红石': '红石 服务'
}


class CustomAPIConfig:
    """自定义API配置管理"""
    
    def __init__(self):
        self.models = PRECONFIGURED_MODELS.copy()
        self._load_from_settings()
    
    def _load_from_settings(self):
        """从设置中加载自定义配置"""
        if settings.custom_api_configs:
            try:
                custom_configs = json.loads(settings.custom_api_configs)
                if isinstance(custom_configs, list):
                    self.models.extend(custom_configs)
            except json.JSONDecodeError:
                print("警告: 无法解析自定义API配置JSON")
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """获取所有模型配置"""
        return self.models
    
    def get_active_models(self) -> List[Dict[str, Any]]:
        """获取活跃的模型配置"""
        return [model for model in self.models if model.get('is_active', True)]
    
    def get_model_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取模型配置"""
        for model in self.models:
            if model['name'] == name:
                return model
        return None
    
    def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """根据供应商获取模型配置"""
        return [model for model in self.models if model.get('provider') == provider]
    
    def add_model(self, model_config: Dict[str, Any]) -> bool:
        """添加新模型配置"""
        try:
            # 验证必需的字段
            required_fields = ['name', 'provider', 'model_name', 'api_base_url', 'api_key']
            for field in required_fields:
                if field not in model_config:
                    print(f"错误: 缺少必需字段 {field}")
                    return False
            
            # 设置默认值
            model_config.setdefault('headers', {})
            model_config.setdefault('parameters', {
                'temperature': 0.7,
                'max_tokens': 2000,
                'stream': False
            })
            model_config.setdefault('is_active', True)
            
            self.models.append(model_config)
            return True
        except Exception as e:
            print(f"添加模型配置失败: {e}")
            return False
    
    def update_model(self, name: str, updates: Dict[str, Any]) -> bool:
        """更新模型配置"""
        for i, model in enumerate(self.models):
            if model['name'] == name:
                self.models[i].update(updates)
                return True
        return False
    
    def remove_model(self, name: str) -> bool:
        """移除模型配置"""
        for i, model in enumerate(self.models):
            if model['name'] == name:
                del self.models[i]
                return True
        return False
    
    def get_provider_description(self, provider: str) -> str:
        """获取供应商描述"""
        return PROVIDER_DESCRIPTIONS.get(provider, f"{provider} 服务")


# 全局自定义API配置实例
custom_api_config = CustomAPIConfig()
