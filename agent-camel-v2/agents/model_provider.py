"""
Model Provider for Agent-Camel V2.
Supports multiple model providers including OpenAI, Anthropic, and Ollama.
Agent-Camel V2的模型提供商。
支持多种模型提供商，包括OpenAI、Anthropic和Ollama。
"""
import openai
import requests
import json
from typing import Dict, Any, Optional
from config.settings import settings

# 导入comet监控器
from agents.comet_monitor import comet_monitor


class ModelProvider:
    """Base class for model providers.
    模型提供商的基类"""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the model.
        使用模型生成文本"""
        raise NotImplementedError


class OpenAIProvider(ModelProvider):
    """OpenAI model provider.
    OpenAI模型提供商"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using OpenAI API.
        使用OpenAI API生成文本
        """
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', settings.DEFAULT_MODEL_NAME),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', settings.MAX_TOKENS),
                temperature=kwargs.get('temperature', settings.TEMPERATURE)
            )
            content = response.choices[0].message.content
            
            # 记录模型调用到Comet ML
            comet_monitor.log_model_call(
                provider_name="openai",
                prompt=prompt,
                response=content,
                model=kwargs.get('model', settings.DEFAULT_MODEL_NAME),
                temperature=kwargs.get('temperature', settings.TEMPERATURE),
                max_tokens=kwargs.get('max_tokens', settings.MAX_TOKENS)
            )
            
            return content
        except Exception as e:
            error_msg = f"Error generating response with OpenAI: {str(e)}"
            
            # 记录错误到Comet ML
            comet_monitor.log_model_call(
                provider_name="openai",
                prompt=prompt,
                response=error_msg,
                model=kwargs.get('model', settings.DEFAULT_MODEL_NAME),
                temperature=kwargs.get('temperature', settings.TEMPERATURE),
                max_tokens=kwargs.get('max_tokens', settings.MAX_TOKENS),
                error=str(e)
            )
            
            return error_msg


class OllamaProvider(ModelProvider):
    """Ollama model provider for local models.
    用于本地模型的Ollama模型提供商"""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Ollama API.
        使用Ollama API生成文本
        """
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": kwargs.get('model', settings.OLLAMA_MODEL_NAME),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', settings.TEMPERATURE)
                }
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get('response', '')
            
            # 记录模型调用到Comet ML
            comet_monitor.log_model_call(
                provider_name="ollama",
                prompt=prompt,
                response=content,
                model=kwargs.get('model', settings.OLLAMA_MODEL_NAME),
                temperature=kwargs.get('temperature', settings.TEMPERATURE)
            )
            
            return content
        except Exception as e:
            error_msg = f"Error generating response with Ollama: {str(e)}"
            
            # 记录错误到Comet ML
            comet_monitor.log_model_call(
                provider_name="ollama",
                prompt=prompt,
                response=error_msg,
                model=kwargs.get('model', settings.OLLAMA_MODEL_NAME),
                temperature=kwargs.get('temperature', settings.TEMPERATURE),
                error=str(e)
            )
            
            return error_msg


class ModelProviderFactory:
    """Factory for creating model providers.
    创建模型提供商的工厂类"""
    
    @staticmethod
    def get_provider(provider_name: str) -> ModelProvider:
        """
        Get a model provider by name.
        根据名称获取模型提供商
        
        Args:
            provider_name: Name of the provider (openai, ollama, anthropic)
                       提供商名称（openai、ollama、anthropic）
            
        Returns:
            ModelProvider instance
            ModelProvider实例
        """
        if provider_name.lower() == "openai":
            return OpenAIProvider()
        elif provider_name.lower() == "ollama":
            return OllamaProvider()
        elif provider_name.lower() == "anthropic":
            # For now, we'll implement a basic version
            # 目前，我们将实现一个基本版本
            # In a full implementation, we would integrate with Anthropic's API
            # 在完整实现中，我们将与Anthropic的API集成
            return AnthropicProvider()
        else:
            # Default to OpenAI
            # 默认使用OpenAI
            return OpenAIProvider()


class AnthropicProvider(ModelProvider):
    """Anthropic model provider.
    Anthropic模型提供商"""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic API.
        使用Anthropic API生成文本"""
        try:
            # Placeholder implementation
            # 占位符实现
            # In a real implementation, we would integrate with Anthropic's API
            # 在实际实现中，我们将与Anthropic的API集成
            content = f"Anthropic provider placeholder response for: {prompt}"
            
            # 记录模型调用到Comet ML
            comet_monitor.log_model_call(
                provider_name="anthropic",
                prompt=prompt,
                response=content,
                model=kwargs.get('model', settings.ANTHROPIC_MODEL_NAME),
                temperature=kwargs.get('temperature', settings.TEMPERATURE)
            )
            
            return content
        except Exception as e:
            error_msg = f"Error generating response with Anthropic: {str(e)}"
            
            # 记录错误到Comet ML
            comet_monitor.log_model_call(
                provider_name="anthropic",
                prompt=prompt,
                response=error_msg,
                model=kwargs.get('model', settings.ANTHROPIC_MODEL_NAME),
                temperature=kwargs.get('temperature', settings.TEMPERATURE),
                error=str(e)
            )
            
            return error_msg