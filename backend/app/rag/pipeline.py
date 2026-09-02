"""RAG 流水线：Document -> Parser -> Chunk -> Embedding -> Vector DB。"""
import hashlib
from pathlib import Path

from .chunker import chunk_text
from .embeddings import embed_query, embed_texts
from .parsers import parse_document
from .vectorstore import ensure_collection, upsert_chunks


async def ingest_file(path: Path, title: str | None = None) -> tuple[str, str, int]:
    """解析单个文件并写入向量库，返回 (doc_id, title, chunks)。"""
    await ensure_collection()
    text = parse_document(path)
    doc_id = hashlib.sha1(str(path).encode()).hexdigest()[:16]
    title = title or path.stem
    chunks = chunk_text(text)
    if not chunks:
        return doc_id, title, 0
    vectors = await embed_texts(chunks)
    await upsert_chunks(doc_id, title, vectors, chunks)
    return doc_id, title, len(chunks)


async def retrieve(question: str, doc_id: str | None = None, limit: int = 6) -> list[dict]:
    await ensure_collection()
    vec = await embed_query(question)
    return await search(vec, limit=limit, doc_id=doc_id)
