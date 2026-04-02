"""
将 uvicorn / fastapi 的标准库 logging 拦截并转发给 loguru。
在 create_app() 或 lifespan 之前调用 setup_logging() 即可。
"""

import logging

from loguru import logger


class _InterceptHandler(logging.Handler):
    """将标准库 logging 的记录转发给 loguru。"""

    def emit(self, record: logging.LogRecord) -> None:
        # 找到对应的 loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 找到真实的调用栈帧，跳过 logging 内部帧
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """接管 uvicorn / fastapi 的日志输出到 loguru。"""
    intercept = _InterceptHandler()

    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
    ):
        log = logging.getLogger(name)
        log.handlers = [intercept]
        log.propagate = False
