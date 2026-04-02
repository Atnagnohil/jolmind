import os

from src.config import config
from src.utils.logger import logger


def init_langsmith() -> None:
    """初始化 LangSmith 追踪，配置来自 config.yaml 的 langsmith 块。"""
    ls = config.langsmith
    if not ls.enabled:
        return
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = ls.api_key
    os.environ["LANGCHAIN_PROJECT"] = ls.project
    os.environ["LANGCHAIN_ENDPOINT"] = ls.endpoint
    logger.info(f"LangSmith 已启用，项目：{ls.project}")
