from datetime import datetime

from sqlalchemy.orm import Session

from src.db.models import User


def create_user(db: Session, nickname: str, avatar: str = "") -> User:
    """创建用户"""
    user = User(nickname=nickname, avatar=avatar)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    """根据 ID 查询用户"""
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    """查询用户列表"""
    return db.query(User).order_by(User.create_time.asc()).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, nickname: str | None = None, avatar: str | None = None) -> User | None:
    """更新用户信息"""
    user = get_user(db, user_id)
    if not user:
        return None
    if nickname is not None:
        user.nickname = nickname
    if avatar is not None:
        user.avatar = avatar
    user.update_time = datetime.now()
    db.commit()
    db.refresh(user)
    return user
