from typing import Optional

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    supplier_code: str = Field(..., description="供应商编码")
    supplier_name: str = Field(..., description="供应商名称")
    contact_name: Optional[str] = Field(None, description="联系人")
    phone: Optional[str] = Field(None, description="联系电话")
    settlement_cycle: int = Field(30, description="结算周期(天)")
    status: bool = Field(True, description="状态")
    address: Optional[str] = Field(None, description="地址")
    remark: Optional[str] = Field(None, description="备注")


class SupplierUpdate(BaseModel):
    id: int
    supplier_code: Optional[str] = Field(None, description="供应商编码")
    supplier_name: Optional[str] = Field(None, description="供应商名称")
    contact_name: Optional[str] = Field(None, description="联系人")
    phone: Optional[str] = Field(None, description="联系电话")
    settlement_cycle: Optional[int] = Field(None, description="结算周期(天)")
    status: Optional[bool] = Field(None, description="状态")
    address: Optional[str] = Field(None, description="地址")
    remark: Optional[str] = Field(None, description="备注")
