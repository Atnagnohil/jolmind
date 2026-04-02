from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import MessageCreate, MessageOut, Response
from src.db.crud import create_message, delete_message, get_message, list_messages

router = APIRouter(prefix="/sessions/{session_id}/messages", tags=["消息"])


@router.post("", response_model=Response[MessageOut], status_code=201)
def create(session_id: str, body: MessageCreate, db: Session = Depends(get_db)):
    message = create_message(
        db,
        user_id=body.user_id,
        session_id=session_id,
        role=body.role,
        content=body.content,
        tool_call_id=body.tool_call_id,
        token_count=body.token_count,
    )
    return Response.ok(message)


@router.get("", response_model=Response[list[MessageOut]])
def list_by_session(session_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Response.ok(list_messages(db, session_id=session_id, skip=skip, limit=limit))


@router.get("/{message_id}", response_model=Response[MessageOut])
def get_one(session_id: str, message_id: int, db: Session = Depends(get_db)):
    message = get_message(db, message_id)
    if not message or message.session_id != session_id:
        raise HTTPException(status_code=404, detail="消息不存在")
    return Response.ok(message)


@router.delete("/{message_id}", response_model=Response[None])
def delete(session_id: str, message_id: int, db: Session = Depends(get_db)):
    message = get_message(db, message_id)
    if not message or message.session_id != session_id:
        raise HTTPException(status_code=404, detail="消息不存在")
    delete_message(db, message_id)
    return Response.ok()
