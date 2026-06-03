from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(..., description="角色")
    content: str = Field(..., min_length=1, description="消息内容")


class AIChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户提问")
    messages: list[ChatMessage] = Field(default_factory=list, description="历史对话")
    store_id: Optional[int] = Field(None, description="门店ID(可选)")

