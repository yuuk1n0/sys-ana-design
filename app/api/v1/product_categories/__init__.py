from fastapi import APIRouter

from .product_categories import router

product_categories_router = APIRouter()
product_categories_router.include_router(router, tags=["商品分类模块"])

__all__ = ["product_categories_router"]
