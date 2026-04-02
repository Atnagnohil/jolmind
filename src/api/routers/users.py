from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import Response, UserOut, UserUpdate
from src.db.crud import get_user, list_users, update_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("", response_model=Response[list[UserOut]])
def get_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return Response.ok(list_users(db, skip=skip, limit=limit))


@router.get("/{user_id}", response_model=Response[UserOut])
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response.ok(user)


@router.patch("/{user_id}", response_model=Response[UserOut])
def patch_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    user = update_user(db, user_id, nickname=body.nickname, avatar=body.avatar)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response.ok(user)
