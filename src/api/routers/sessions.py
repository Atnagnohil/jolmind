from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import Response, SessionCreate, SessionOut, SessionUpdate
from src.db.crud import (
    close_session,
    create_session,
    delete_session,
    get_session,
    list_sessions,
    update_session,
)

router = APIRouter(prefix="/sessions", tags=["会话"])


@router.post("", response_model=Response[SessionOut], status_code=201)
def create(body: SessionCreate, db: Session = Depends(get_db)):
    session = create_session(db, user_id=body.user_id, session_name=body.session_name, remark=body.remark)
    return Response.ok(session)


@router.get("", response_model=Response[list[SessionOut]])
def list_by_user(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return Response.ok(list_sessions(db, user_id=user_id, skip=skip, limit=limit))


@router.get("/{session_id}", response_model=Response[SessionOut])
def get_one(session_id: str, db: Session = Depends(get_db)):
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return Response.ok(session)


@router.patch("/{session_id}", response_model=Response[SessionOut])
def patch(session_id: str, body: SessionUpdate, db: Session = Depends(get_db)):
    session = update_session(
        db, session_id,
        session_name=body.session_name,
        session_status=body.session_status,
        remark=body.remark,
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return Response.ok(session)


@router.patch("/{session_id}/close", response_model=Response[SessionOut])
def close(session_id: str, db: Session = Depends(get_db)):
    session = close_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return Response.ok(session)


@router.delete("/{session_id}", response_model=Response[None])
def delete(session_id: str, db: Session = Depends(get_db)):
    if not delete_session(db, session_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return Response.ok()
