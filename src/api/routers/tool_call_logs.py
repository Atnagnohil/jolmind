from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import Response, ToolCallLogOut
from src.db.crud import get_tool_call_log, list_tool_call_logs

router = APIRouter(prefix="/tool-call-logs", tags=["工具调用日志"])


@router.get("", response_model=Response[list[ToolCallLogOut]])
def list_logs(
    session_id: str | None = None,
    tool_name: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return Response.ok(list_tool_call_logs(db, session_id=session_id, tool_name=tool_name, skip=skip, limit=limit))


@router.get("/{log_id}", response_model=Response[ToolCallLogOut])
def get_one(log_id: int, db: Session = Depends(get_db)):
    log = get_tool_call_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return Response.ok(log)
