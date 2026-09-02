"""Agent 接口：列出可用 Agent。"""
from fastapi import APIRouter

from ..agent.router import PROFILES

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("")
def list_agents():
    return [
        {"name": p["name"], "key": key, "desc": p["desc"]}
        for key, p in PROFILES.items()
    ]
