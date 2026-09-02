"""Embedding 客户端：使用 OpenAI 兼容接口。"""
from openai import AsyncOpenAI

from ..config import get_settings

settings = get_settings()
_client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    resp = await _client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    return [item.embedding for item in resp.data]


async def embed_query(text: str) -> list[float]:
    (vec,) = await embed_texts([text])
    return vec
