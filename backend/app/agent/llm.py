"""LLM 客户端：OpenAI 兼容 chat 接口。"""
from openai import AsyncOpenAI

from ..config import get_settings

settings = get_settings()
_client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)


async def chat_completion(messages: list[dict], model: str | None = None) -> str:
    resp = await _client.chat.completions.create(
        model=model or settings.llm_model,
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content or ""
