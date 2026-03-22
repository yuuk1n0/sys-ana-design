from typing import Optional

from pydantic import BaseModel, Field


class ProductCategoryCreate(BaseModel):
    name: str = Field(..., description="分类名称")
    sort: int = Field(0, description="排序")
    status: bool = Field(True, description="状态")


class ProductCategoryUpdate(BaseModel):
    id: int
    name: Optional[str] = Field(None, description="分类名称")
    sort: Optional[int] = Field(None, description="排序")
    status: Optional[bool] = Field(None, description="状态")
