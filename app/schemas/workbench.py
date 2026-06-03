from typing import Optional

from pydantic import BaseModel, Field


class WorkbenchDashboardQuery(BaseModel):
    days: int = Field(7, ge=1, le=31, description="趋势天数")


class WorkbenchDashboardResponse(BaseModel):
    generated_at: str = Field(..., description="生成时间")
    store_id: Optional[int] = Field(None, description="当前门店ID")
    store_name: str = Field(..., description="当前门店名称")
    data: dict = Field(..., description="驾驶舱数据")

