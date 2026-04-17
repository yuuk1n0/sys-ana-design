from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class StoreEmployeeCreate(BaseModel):
    employee_no: str = Field(..., description="员工工号")
    name: str = Field(..., description="员工姓名")
    phone: Optional[str] = Field(None, description="手机号")
    job_title: str = Field(..., description="岗位")
    hire_date: Optional[date] = Field(None, description="入职日期")
    status: bool = Field(True, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class StoreEmployeeUpdate(BaseModel):
    id: int
    employee_no: Optional[str] = Field(None, description="员工工号")
    name: Optional[str] = Field(None, description="员工姓名")
    phone: Optional[str] = Field(None, description="手机号")
    job_title: Optional[str] = Field(None, description="岗位")
    hire_date: Optional[date] = Field(None, description="入职日期")
    status: Optional[bool] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")
