"""RAG 接口：/api/rag/chat、/api/rag/summary。"""
from fastapi import APIRouter

from ..agent.router import route_agent, run_agent
from ..agent.llm import chat_completion
from ..models.schemas import ChatRequest, ChatResponse, Source, SummaryRequest
from ..rag.pipeline import retrieve

router = APIRouter(prefix="/rag", tags=["rag"])

_SUMMARY_SYSTEM = "你是专业的内容总结助手。请基于给定文本输出简洁、准确、结构化的中文摘要。"


@router.post("/chat", response_model=ChatResponse)
async def rag_chat(req: ChatRequest):
    agent_name = route_agent(req)
    sources = await retrieve(req.question, doc_id=req.book_id)
    answer = await run_agent(agent_name, req.question, sources)
    seen: set[str] = set()
    uniq: list[Source] = []
    for s in sources:
        if s["title"] not in seen:
            seen.add(s["title"])
            uniq.append(Source(title=s["title"], locator=f"{s['doc_id']}#chunk-{s.get('chunk', 0)}"))
    return ChatResponse(answer=answer, sources=uniq, agent=agent_name)


@router.post("/summary", response_model=ChatResponse)
async def rag_summary(req: SummaryRequest):
    messages = [
        {"role": "system", "content": _SUMMARY_SYSTEM},
        {"role": "user", "content": f"请总结以下内容：\n\n{req.text[:12000]}"},
    ]
    answer = await chat_completion(messages)
    return ChatResponse(answer=answer, sources=[])
