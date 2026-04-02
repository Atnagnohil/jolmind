import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiosqlite
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.config import config
from src.providers.llm.registry import registry


def get_summarization_middleware(
        model: BaseChatModel | None = None,
        trigger: tuple | list | None = ("tokens", 4000),
        keep: tuple = ("messages", 20),
) -> SummarizationMiddleware:
    """获取总结中间件。"""
    if model is None:
        provider = registry.create(provider_name=config.llm.default)
        model = provider.get_model()
    return SummarizationMiddleware(model=model, trigger=trigger, keep=keep)


class SaverFactory:
    _saver: AsyncSqliteSaver | None = None
    _conn: aiosqlite.Connection | None = None

    @classmethod
    async def open(cls) -> None:
        """应用启动时调用，初始化全局异步 saver 实例。"""
        if cls._saver is None:
            cls._conn = await aiosqlite.connect(config.memory.sqlite_path)
            cls._saver = AsyncSqliteSaver(cls._conn)

    @classmethod
    async def close(cls) -> None:
        """应用关闭时调用，释放连接。"""
        if cls._conn is not None:
            await cls._conn.close()
            cls._conn = None
            cls._saver = None

    @classmethod
    def get_saver(cls) -> AsyncSqliteSaver:
        """获取全局 saver 实例，需先调用 await open()。"""
        if cls._saver is None:
            raise RuntimeError("SaverFactory 未初始化，请先调用 await SaverFactory.open()")
        return cls._saver

    @staticmethod
    @asynccontextmanager
    async def scoped_saver() -> AsyncIterator[AsyncSqliteSaver]:
        """短生命周期场景使用，自动管理连接开关。"""
        conn = await aiosqlite.connect(config.memory.sqlite_path)
        try:
            yield AsyncSqliteSaver(conn)
        finally:
            await conn.close()
