from typing import Optional

from pydantic import BaseModel, Field


class SalesOrderItemCreate(BaseModel):
    product_id: int = Field(..., description="商品ID")
    qty: int = Field(..., gt=0, description="数量")


class SalesOrderCreate(BaseModel):
    member_id: Optional[int] = Field(None, description="会员ID")
    remark: Optional[str] = Field(None, description="备注")
    items: list[SalesOrderItemCreate] = Field(..., min_length=1, description="销售/退货明细")
