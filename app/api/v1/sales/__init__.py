from fastapi import APIRouter

from .sales import router

sales_router = APIRouter()
sales_router.include_router(router, tags=["销售模块"])

__all__ = ["sales_router"]
