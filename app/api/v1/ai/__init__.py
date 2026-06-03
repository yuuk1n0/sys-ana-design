from fastapi import APIRouter

from .ai import router

ai_router = APIRouter()
ai_router.include_router(router, tags=["AI经营分析"])

__all__ = ["ai_router"]

