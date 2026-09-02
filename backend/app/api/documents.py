"""文档摄取接口：上传 / 批量入库本地 library 文件。"""
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select

from ..models.db import Base, Document, SessionLocal, engine
from ..models.schemas import IngestResponse
from ..rag.pipeline import ingest_file

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("/data/uploads")


@router.post("/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".epub", ".md", ".markdown", ".txt"}:
        raise HTTPException(400, f"不支持的格式: {suffix}")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = UPLOAD_DIR / (file.filename or "unnamed")
    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    doc_id, title, chunks = await ingest_file(target)

    with SessionLocal() as session:
        row = session.execute(
            select(Document).where(Document.doc_id == doc_id)
        ).scalar_one_or_none()
        if row is None:
            row = Document(doc_id=doc_id, title=title, path=str(target), format=suffix.lstrip("."))
            session.add(row)
        row.chunks = chunks
        session.commit()

    return IngestResponse(doc_id=doc_id, title=title, chunks=chunks)


@router.get("")
def list_documents():
    with SessionLocal() as session:
        rows = session.execute(select(Document).order_by(Document.id)).scalars().all()
        return [
            {
                "doc_id": r.doc_id,
                "title": r.title,
                "format": r.format,
                "chunks": r.chunks,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]


@router.post("/init-db")
def init_db():
    Base.metadata.create_all(engine)
    return {"ok": True}
