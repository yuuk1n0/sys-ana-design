from typing import Optional

from pydantic import BaseModel, Field


class MemberCreate(BaseModel):
    member_no: str = Field(..., description="会员编号")
    name: str = Field(..., description="会员姓名")
    phone: Optional[str] = Field(None, description="手机号")
    level: str = Field("NORMAL", description="会员等级")
    points: int = Field(0, description="积分")
    status: bool = Field(True, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class MemberUpdate(BaseModel):
    id: int
    member_no: Optional[str] = Field(None, description="会员编号")
    name: Optional[str] = Field(None, description="会员姓名")
    phone: Optional[str] = Field(None, description="手机号")
    level: Optional[str] = Field(None, description="会员等级")
    points: Optional[int] = Field(None, description="积分")
    status: Optional[bool] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")
