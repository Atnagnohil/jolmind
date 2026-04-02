from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import config

engine = create_engine(
    config.db.url,
    pool_pre_ping=True,   # 自动检测断连
    pool_recycle=3600,    # 连接复用 1 小时后回收，防止 MySQL 8h 超时断开
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
