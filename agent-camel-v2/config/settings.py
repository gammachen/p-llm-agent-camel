"""
Configuration settings for Agent-Camel V2.
Agent-Camel V2的配置设置
"""
import os
from typing import Optional


class Settings:
    # LLM settings
    # LLM设置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Database settings
    # 数据库设置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost/db")
    
    # Vector database settings
    # 向量数据库设置
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    
    # Model settings
    # 模型设置
    DEFAULT_MODEL_PROVIDER: str = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    DEFAULT_MODEL_NAME: str = os.getenv("DEFAULT_MODEL_NAME", "gpt-3.5-turbo")
    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "llama2")
    
    # Performance settings
    # 性能设置
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # Monitoring settings
    # 监控设置
    COMET_API_KEY: Optional[str] = os.getenv("COMET_API_KEY")
    COMET_PROJECT_NAME: str = os.getenv("COMET_PROJECT_NAME", "camel-agent-monitoring")
    COMET_WORKSPACE: Optional[str] = os.getenv("COMET_WORKSPACE", "comet-workspace-0811")
    COMET_LOG_MODEL_CALLS: bool = os.getenv("COMET_LOG_MODEL_CALLS", "True").lower() == "true"

settings = Settings()