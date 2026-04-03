from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, JSON, SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户表"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="用户主键ID")
    avatar: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="用户头像URL")
    nickname: Mapped[str] = mapped_column(String(64), nullable=False, default="", comment="用户昵称")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class ChatSession(Base):
    __tablename__ = "chat_session"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        {"comment": "对话会话表"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, comment="会话主键ID（UUID）")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="关联用户ID")
    session_name: Mapped[str] = mapped_column(String(64), nullable=False, default="新会话", comment="会话名称")
    session_status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, comment="会话状态 0-关闭 1-进行中")
    remark: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="会话备注")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="逻辑删除 0-未删除 1-已删除")


class ToolCallLog(Base):
    __tablename__ = "tool_call_log"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_session_id", "session_id"),
        Index("idx_tool_name", "tool_name"),
        {"comment": "工具调用日志表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="日志主键ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="操作用户ID")
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, comment="关联会话ID")
    tool_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="工具名称")
    call_params: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="调用入参（JSON格式）")
    call_result: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="调用返回结果（JSON格式）")
    call_status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, comment="调用状态 0-失败 1-成功")
    cost_time: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="调用耗时（毫秒）")
    error_msg: Mapped[str] = mapped_column(String(512), nullable=False, default="", comment="失败错误信息")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="逻辑删除 0-未删除 1-已删除")


class ChatMessage(Base):
    __tablename__ = "chat_message"
    __table_args__ = (
        Index("idx_session_id", "session_id"),
        Index("idx_user_id", "user_id"),
        {"comment": "对话消息表"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="消息主键ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="关联用户ID")
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, comment="关联会话ID")
    role: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="消息角色 0-user 1-assistant 2-tool 3-thinking")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    tool_call_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="关联工具调用日志ID")
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="消息token数")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="逻辑删除 0-未删除 1-已删除")
