from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    category_id: int = Field(..., description="分类ID")
    product_code: str = Field(..., description="商品编码")
    name: str = Field(..., description="商品名称")
    unit: str = Field(..., description="单位")
    sale_price: Decimal = Field(..., description="售价")
    barcode: Optional[str] = Field(None, description="条码")
    low_stock_threshold: int = Field(0, description="预警阈值")
    status: bool = Field(True, description="上架状态")
    remark: Optional[str] = Field(None, description="备注")


class ProductUpdate(BaseModel):
    id: int
    category_id: Optional[int] = Field(None, description="分类ID")
    product_code: Optional[str] = Field(None, description="商品编码")
    name: Optional[str] = Field(None, description="商品名称")
    unit: Optional[str] = Field(None, description="单位")
    sale_price: Optional[Decimal] = Field(None, description="售价")
    barcode: Optional[str] = Field(None, description="条码")
    low_stock_threshold: Optional[int] = Field(None, description="预警阈值")
    status: Optional[bool] = Field(None, description="上架状态")
    remark: Optional[str] = Field(None, description="备注")


class ProductStatusUpdate(BaseModel):
    id: int = Field(..., description="商品ID")
    status: bool = Field(..., description="状态")
