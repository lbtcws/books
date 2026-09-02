"""Qdrant 向量库封装。"""
import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..config import get_settings

settings = get_settings()

client = AsyncQdrantClient(url=settings.qdrant_url)


async def ensure_collection() -> None:
    if not await client.collection_exists(settings.qdrant_collection):
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
        )


async def delete_document(doc_id: str) -> None:
    await client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=FilterSelector(
            filter=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))])
        ),
    )


def _point_id(doc_id: str, idx: int) -> str:
    # Qdrant 要求 UUID/整数主键，用命名空间 UUID 保证跨文档唯一且幂等
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}:{idx}"))


async def upsert_chunks(doc_id: str, title: str, vectors: list[list[float]], chunks: list[str]) -> None:
    points = [
        PointStruct(
            id=_point_id(doc_id, i),
            vector=vec,
            payload={"doc_id": doc_id, "title": title, "text": text, "chunk": i},
        )
        for i, (vec, text) in enumerate(zip(vectors, chunks))
    ]
    await client.upsert(collection_name=settings.qdrant_collection, points=points)


async def search(query_vector: list[float], limit: int = 6, doc_id: str | None = None) -> list[dict]:
    must = []
    if doc_id:
        must.append(FieldCondition(key="doc_id", match=MatchValue(value=doc_id)))
    res = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=limit,
        query_filter=Filter(must=must) if must else None,
        with_payload=True,
    )
    return [
        {
            "title": p.payload.get("title", ""),
            "doc_id": p.payload.get("doc_id", ""),
            "chunk": p.payload.get("chunk", 0),
            "text": p.payload.get("text", ""),
            "score": p.score,
        }
        for p in res.points
    ]
