"""文本切片：按字符窗口 + 重叠切分，优先在句子边界断开。"""
import re

from ..config import get_settings

settings = get_settings()

_SENTENCE = re.compile(r"(?<=[。！？.!?])\s+")


def split_sentences(text: str) -> list[str]:
    parts = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        parts.extend(s.strip() for s in _SENTENCE.split(para) if s.strip())
    return parts


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    size = chunk_size or settings.chunk_size
    ov = overlap or settings.chunk_overlap
    sentences = split_sentences(text)

    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0
    for sent in sentences:
        buf.append(sent)
        buf_len += len(sent)
        if buf_len >= size:
            chunks.append("".join(buf))
            # 保留尾部句子作为重叠上下文
            carry: list[str] = []
            carry_len = 0
            for s in reversed(buf):
                if carry_len + len(s) > ov:
                    break
                carry.insert(0, s)
                carry_len += len(s)
            buf = carry
            buf_len = carry_len
    if buf:
        chunks.append("".join(buf))
    return chunks
