"""Multi-Agent：Reader / Knowledge / Investment / Assistant + Router。"""
from ..models.schemas import ChatRequest
from .llm import chat_completion

PROFILES: dict[str, dict] = {
    "reader": {
        "name": "Reader Agent",
        "desc": "阅读总结：提炼书籍/章节要点、人物关系、核心论点",
        "system": (
            "你是深度阅读助手。基于给定资料回答问题，输出结构清晰的要点总结。"
            "资料不足时明确说明，不要编造。用中文回答。"
        ),
    },
    "knowledge": {
        "name": "Knowledge Agent",
        "desc": "知识检索：跨书籍概念关联、对比、溯源",
        "system": (
            "你是知识库检索助手。综合多来源资料回答问题，标注每条信息的出处标题。"
            "资料不足时明确说明。用中文回答。"
        ),
    },
    "investment": {
        "name": "Investment Agent",
        "desc": "投资分析：财务指标、估值逻辑、投资大师思想",
        "system": (
            "你是投资研究助手，熟悉价值投资框架（巴菲特/芒格）。"
            "基于资料分析投资相关问题，给出论据与风险提示，不构成投资建议。用中文回答。"
        ),
    },
    "assistant": {
        "name": "Assistant Agent",
        "desc": "个人助手：日程、决策记录、综合事务",
        "system": (
            "你是个人知识管理助手。基于用户资料库回答综合性问题，"
            "必要时给出下一步行动建议。用中文回答。"
        ),
    },
}

# 关键词路由规则（轻量启发式；生产可换成 LLM 分类）
_KEYWORDS: dict[str, tuple[str, ...]] = {
    "investment": ("股票", "估值", "财报", "投资", "巴菲特", "芒格", "护城河", "市盈率", "基金", "仓位"),
    "reader": ("总结", "讲了什么", "概括", "梗概", "章节", "人物", "读后感", "主要内容"),
    "knowledge": ("哪些书", "关联", "对比", "出处", "概念", "定义", "关系"),
}


def route_agent(req: ChatRequest) -> str:
    """Agent Router：显式指定优先，否则按关键词打分选择。"""
    if req.agent and req.agent in PROFILES:
        return req.agent
    q = req.question
    scores = {
        name: sum(1 for kw in kws if kw in q)
        for name, kws in _KEYWORDS.items()
    }
    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    return best if scores[best] > 0 else "assistant"


def build_context(sources: list[dict]) -> str:
    blocks = [
        f"[资料{i + 1}｜{s['title']}]\n{s['text']}" for i, s in enumerate(sources)
    ]
    return "\n\n".join(blocks) if blocks else "（知识库中未检索到相关内容）"


async def run_agent(agent_name: str, question: str, sources: list[dict]) -> str:
    profile = PROFILES[agent_name]
    messages = [
        {"role": "system", "content": profile["system"]},
        {
            "role": "user",
            "content": f"参考资料：\n\n{build_context(sources)}\n\n问题：{question}",
        },
    ]
    return await chat_completion(messages)
