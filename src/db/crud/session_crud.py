import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.db.models import ChatSession


def create_session(db: Session, user_id: int, session_name: str = "新会话", remark: str = "") -> ChatSession:
    """创建新会话"""
    session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        session_name=session_name,
        remark=remark,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: str) -> ChatSession | None:
    """根据 ID 查询会话"""
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.is_deleted == 0)
        .first()
    )


def list_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[ChatSession]:
    """查询用户的会话列表，按创建时间倒序"""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id, ChatSession.is_deleted == 0)
        .order_by(ChatSession.create_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_session(
    db: Session,
    session_id: str,
    session_name: str | None = None,
    session_status: int | None = None,
    remark: str | None = None,
) -> ChatSession | None:
    """更新会话信息"""
    session = get_session(db, session_id)
    if not session:
        return None
    if session_name is not None:
        session.session_name = session_name
    if session_status is not None:
        session.session_status = session_status
    if remark is not None:
        session.remark = remark
    session.update_time = datetime.now()
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: str) -> bool:
    """逻辑删除会话"""
    session = get_session(db, session_id)
    if not session:
        return False
    session.is_deleted = 1
    session.update_time = datetime.now()
    db.commit()
    return True


def close_session(db: Session, session_id: str) -> ChatSession | None:
    """关闭会话（status -> 0）"""
    return update_session(db, session_id, session_status=0)
