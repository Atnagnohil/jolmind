from datetime import datetime

from sqlalchemy.orm import Session

from src.db.models import ChatMessage


def create_message(
    db: Session,
    user_id: int,
    session_id: str,
    role: int,
    content: str,
    tool_call_id: int | None = None,
    token_count: int = 0,
) -> ChatMessage:
    """创建消息"""
    message = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        tool_call_id=tool_call_id,
        token_count=token_count,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_message(db: Session, message_id: int) -> ChatMessage | None:
    """根据 ID 查询消息"""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.id == message_id, ChatMessage.is_deleted == 0)
        .first()
    )


def list_messages(db: Session, session_id: str, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
    """查询会话的消息列表，按创建时间正序"""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.is_deleted == 0)
        .order_by(ChatMessage.create_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_message(db: Session, message_id: int) -> bool:
    """逻辑删除消息"""
    message = get_message(db, message_id)
    if not message:
        return False
    message.is_deleted = 1
    message.update_time = datetime.now()
    db.commit()
    return True


def delete_messages_by_session(db: Session, session_id: str) -> int:
    """逻辑删除会话下所有消息，返回影响行数"""
    count = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.is_deleted == 0)
        .update({"is_deleted": 1, "update_time": datetime.now()})
    )
    db.commit()
    return count
