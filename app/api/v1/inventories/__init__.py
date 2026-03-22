from fastapi import APIRouter

from .inventories import router

inventories_router = APIRouter()
inventories_router.include_router(router, tags=["库存模块"])

__all__ = ["inventories_router"]
