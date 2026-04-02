import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

from sqlalchemy.orm import Session

from src.db.models import ToolCallLog


def create_tool_call_log(
    db: Session,
    user_id: int,
    session_id: str,
    tool_name: str,
    call_params: dict | None = None,
    call_result: dict | None = None,
    call_status: int = 1,
    cost_time: int = 0,
    error_msg: str = "",
) -> ToolCallLog:
    """创建工具调用日志"""
    log = ToolCallLog(
        user_id=user_id,
        session_id=session_id,
        tool_name=tool_name,
        call_params=call_params,
        call_result=call_result,
        call_status=call_status,
        cost_time=cost_time,
        error_msg=error_msg,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_tool_call_log(db: Session, log_id: int) -> ToolCallLog | None:
    """根据 ID 查询日志"""
    return (
        db.query(ToolCallLog)
        .filter(ToolCallLog.id == log_id, ToolCallLog.is_deleted == 0)
        .first()
    )


def list_tool_call_logs(
    db: Session,
    session_id: str | None = None,
    tool_name: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[ToolCallLog]:
    """查询工具调用日志，支持按会话或工具名过滤"""
    query = db.query(ToolCallLog).filter(ToolCallLog.is_deleted == 0)
    if session_id:
        query = query.filter(ToolCallLog.session_id == session_id)
    if tool_name:
        query = query.filter(ToolCallLog.tool_name == tool_name)
    return query.order_by(ToolCallLog.create_time.desc()).offset(skip).limit(limit).all()


def delete_tool_call_log(db: Session, log_id: int) -> bool:
    """逻辑删除日志"""
    log = get_tool_call_log(db, log_id)
    if not log:
        return False
    log.is_deleted = 1
    log.update_time = datetime.now()
    db.commit()
    return True


@contextmanager
def record_tool_call(
    db: Session,
    user_id: int,
    session_id: str,
    tool_name: str,
    call_params: dict | None = None,
) -> Generator[dict[str, Any], None, None]:
    """
    上下文管理器，自动记录工具调用耗时和结果。

    用法：
        with record_tool_call(db, user_id, session_id, "web_search", {"query": "..."}) as ctx:
            result = do_search()
            ctx["result"] = result
    """
    ctx: dict[str, Any] = {"result": None}
    start = time.monotonic()
    try:
        yield ctx
        cost_time = int((time.monotonic() - start) * 1000)
        create_tool_call_log(
            db, user_id, session_id, tool_name,
            call_params=call_params,
            call_result=ctx["result"],
            call_status=1,
            cost_time=cost_time,
        )
    except Exception as e:
        cost_time = int((time.monotonic() - start) * 1000)
        create_tool_call_log(
            db, user_id, session_id, tool_name,
            call_params=call_params,
            call_status=0,
            cost_time=cost_time,
            error_msg=str(e),
        )
        raise
