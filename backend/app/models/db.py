"""SQLAlchemy 元数据层：文档登记表（Postgres）。"""
from sqlalchemy import JSON, Column, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

from ..config import get_settings

settings = get_settings()

engine = create_engine(settings.postgres_dsn, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(512), nullable=False)
    path = Column(String(1024), nullable=False)
    format = Column(String(16), nullable=False)
    chunks = Column(Integer, default=0)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
