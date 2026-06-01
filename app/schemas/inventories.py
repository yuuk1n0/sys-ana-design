from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InventoryInitTxnCreate(BaseModel):
    product_id: int = Field(..., description="商品ID")
    biz_type: str = Field("INIT", description="业务类型")
    biz_no: str = Field(..., description="业务单号")
    change_qty: int = Field(0, description="变更数量")
    before_qty: int = Field(0, description="变更前")
    after_qty: int = Field(0, description="变更后")
    remark: Optional[str] = Field(None, description="备注")
    operator_id: Optional[int] = Field(None, description="操作人")


class InventoryTxnQuery(BaseModel):
    product_id: Optional[int] = None
    biz_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class InventoryOperateItem(BaseModel):
    product_id: int = Field(..., description="商品ID")
    qty: int = Field(..., gt=0, description="作业数量")


class InventoryOperateCreate(BaseModel):
    biz_type: str = Field(..., description="业务类型: STOCK_IN/STOCK_OUT")
    remark: Optional[str] = Field(None, description="备注")
    items: list[InventoryOperateItem] = Field(..., min_length=1, description="作业明细")
