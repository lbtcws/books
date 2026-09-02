"""请求 / 响应数据模型。"""
from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    book_id: Optional[str] = None
    agent: Optional[str] = None  # reader | knowledge | investment | assistant


class Source(BaseModel):
    title: str
    locator: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    agent: Optional[str] = None


class SummaryRequest(BaseModel):
    text: str
    book_id: Optional[str] = None


class IngestResponse(BaseModel):
    doc_id: str
    title: str
    chunks: int
