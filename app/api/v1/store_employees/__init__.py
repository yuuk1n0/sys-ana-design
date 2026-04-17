from fastapi import APIRouter

from .store_employees import router

store_employees_router = APIRouter()
store_employees_router.include_router(router, tags=["门店员工模块"])

__all__ = ["store_employees_router"]
