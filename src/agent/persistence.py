import time
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from sqlalchemy.orm import Session

from src.db.crud.message_crud import create_message
from src.db.crud.tool_call_log_crud import create_tool_call_log

ROLE_USER = 0
ROLE_ASSISTANT = 1
ROLE_TOOL = 2


def persist_messages(
    db: Session,
    user_id: int,
    session_id: str,
    messages: list[Any],
    start_time: float,
    existing_ids: set[str] | None = None,
) -> None:
    """
    将 LangGraph 返回的消息链持久化到数据库，自动跳过已存在的消息。

    Args:
        db: 数据库 session。
        user_id: 用户 ID。
        session_id: 会话 ID。
        messages: agent.invoke 返回的 result["messages"]（全量历史）。
        start_time: 本次调用开始时间，用于计算工具耗时。
        existing_ids: 上一轮已持久化的消息 ID 集合，用于去重。
    """
    existing_ids = existing_ids or set()
    tool_call_map: dict[str, int] = {}

    for msg in messages:
        # 跳过历史轮次已存储的消息
        if msg.id and msg.id in existing_ids:
            continue

        if isinstance(msg, HumanMessage):
            create_message(
                db,
                user_id=user_id,
                session_id=session_id,
                role=ROLE_USER,
                content=_extract_content(msg.content),
                token_count=_get_tokens(msg),
            )

        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    log = create_tool_call_log(
                        db,
                        user_id=user_id,
                        session_id=session_id,
                        tool_name=tc["name"],
                        call_params=tc.get("args"),
                        call_status=1,
                        cost_time=int((time.monotonic() - start_time) * 1000),
                    )
                    tool_call_map[tc["id"]] = log.id

            content = _extract_content(msg.content)
            if content:
                create_message(
                    db,
                    user_id=user_id,
                    session_id=session_id,
                    role=ROLE_ASSISTANT,
                    content=content,
                    token_count=_get_tokens(msg),
                )

        elif isinstance(msg, ToolMessage):
            tool_log_id = tool_call_map.get(msg.tool_call_id)
            create_message(
                db,
                user_id=user_id,
                session_id=session_id,
                role=ROLE_TOOL,
                content=_extract_content(msg.content),
                tool_call_id=tool_log_id,
            )


def collect_message_ids(messages: list[Any]) -> set[str]:
    """提取消息 ID 集合，在 invoke 前调用，用于下一轮去重。"""
    return {msg.id for msg in messages if msg.id}


def _get_tokens(msg: Any) -> int:
    """从 usage_metadata 提取 token 数。"""
    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
        return msg.usage_metadata.get("total_tokens", 0)
    return 0


def _extract_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            part["text"] for part in content if isinstance(part, dict) and part.get("type") == "text"
        )
    return str(content)
