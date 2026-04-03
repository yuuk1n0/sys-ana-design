from fastapi import APIRouter

from .finances import router

finances_router = APIRouter()
finances_router.include_router(router, tags=["财务模块"])

__all__ = ["finances_router"]
