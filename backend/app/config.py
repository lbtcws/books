"""应用配置：全部通过环境变量注入，提供合理默认值。"""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 服务
    app_name: str = "LBTC AI Knowledge Library Backend"
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000

    # 向量库
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "library"

    # 关系库（元数据 / 文档登记）
    postgres_dsn: str = "postgresql+psycopg://lbtc:lbtc@postgres:5432/lbtc"

    # Embedding / LLM（OpenAI 兼容接口，可指向本地或云端）
    openai_api_key: str = "sk-placeholder"
    openai_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    llm_model: str = "gpt-4o-mini"

    # RAG 切片
    chunk_size: int = 800
    chunk_overlap: int = 120

    # CORS（前端地址）
    cors_origins: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
