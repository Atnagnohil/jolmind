import sqlite3
from contextlib import contextmanager, closing
from typing import Iterator
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.sqlite import SqliteSaver

from src.config import config
from src.providers.llm.registry import registry


def get_summarization_middleware(
        model: BaseChatModel | None = None,
        trigger: tuple | list | None = ("tokens", 4000),
        keep: tuple = ("messages", 20),
) -> SummarizationMiddleware:
    """
    获取总结中间件。

    Args:
        model: 用于生成摘要的语言模型，为 None 时使用默认提供者的默认模型。
        trigger: 触发总结的阈值，例如 ("tokens", 3000) 或 ("fraction", 0.8)。
                 为 None 时使用 langchain 默认行为。
        keep: 总结后保留的上下文量，默认保留最近 20 条消息。

    Returns:
        配置好的 SummarizationMiddleware 实例。
    """
    if model is None:
        provider = registry.create(provider_name=config.llm.default)
        model = provider.get_model()

    return SummarizationMiddleware(
        model=model,
        trigger=trigger,
        keep=keep,
    )


class SaverFactory:
    _saver: SqliteSaver | None = None
    _conn: sqlite3.Connection | None = None

    @classmethod
    def open(cls) -> None:
        """应用启动时调用，初始化全局 saver 实例。"""
        if cls._saver is None:
            cls._conn = sqlite3.connect(
                config.memory.sqlite_path,
                check_same_thread=False,
            )
            cls._saver = SqliteSaver(cls._conn)

    @classmethod
    def close(cls) -> None:
        """应用关闭时调用，释放 SQLite 连接。"""
        if cls._conn is not None:
            cls._conn.close()
            cls._conn = None
            cls._saver = None

    @classmethod
    def get_saver(cls) -> SqliteSaver:
        """获取全局 saver 实例，需先调用 open()。"""
        if cls._saver is None:
            raise RuntimeError("SaverFactory 未初始化，请先调用 SaverFactory.open()")
        return cls._saver

    @staticmethod
    @contextmanager
    def scoped_saver() -> Iterator[BaseCheckpointSaver]:
        """短生命周期场景使用，自动管理连接开关。"""
        with closing(sqlite3.connect(config.memory.sqlite_path, check_same_thread=False)) as conn:
            yield SqliteSaver(conn)
