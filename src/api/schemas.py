from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ── 通用响应包装 ──────────────────────────────────────────
class Response(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None

    @classmethod
    def ok(cls, data: T = None) -> "Response[T]":
        return cls(data=data)

    @classmethod
    def fail(cls, message: str, code: int = 400) -> "Response":
        return cls(code=code, message=message)


# ── User ─────────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    nickname: str
    avatar: str
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nickname: str | None = Field(None, max_length=64)
    avatar: str | None = Field(None, max_length=255)


# ── ChatSession ───────────────────────────────────────────
class SessionCreate(BaseModel):
    user_id: int
    session_name: str = Field("新会话", max_length=64)
    remark: str = Field("", max_length=255)


class SessionUpdate(BaseModel):
    session_name: str | None = Field(None, max_length=64)
    session_status: int | None = Field(None, ge=0, le=1)
    remark: str | None = Field(None, max_length=255)


class SessionOut(BaseModel):
    id: str
    user_id: int
    session_name: str
    session_status: int
    remark: str
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}


# ── ChatMessage ───────────────────────────────────────────
class MessageCreate(BaseModel):
    user_id: int
    role: int = Field(..., ge=0, le=2, description="0-user 1-assistant 2-tool")
    content: str
    tool_call_id: int | None = None
    token_count: int = 0


class MessageOut(BaseModel):
    id: int
    user_id: int
    session_id: str
    role: int
    content: str
    tool_call_id: int | None
    token_count: int
    create_time: datetime

    model_config = {"from_attributes": True}


# ── ToolCallLog ───────────────────────────────────────────
class ToolCallLogOut(BaseModel):
    id: int
    user_id: int
    session_id: str
    tool_name: str
    call_params: dict | None
    call_result: dict | None
    call_status: int
    cost_time: int
    error_msg: str
    create_time: datetime

    model_config = {"from_attributes": True}


# ── 分页 ──────────────────────────────────────────────────
class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
