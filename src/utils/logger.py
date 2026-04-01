"""日志工具模块，基于 Loguru 封装。

参考主流 QQ 机器人框架（如 NoneBot2）的日志设计，提供开箱即用的日志功能。
支持控制台彩色输出、文件按大小/时间轮转，并修复了二次封装导致的调用栈丢失问题。
"""

import sys
from pathlib import Path
from typing import Any, Union

import loguru

from src.config import config

# 导出原生 logger 对象，推荐在其他模块中直接 from src.utils.logger import logger
logger = loguru.logger


def init_logger(
    log_dir: Union[str, Path] = None,
    rotation: str = None,
    retention: str = None,
    console_level: str = None,
    file_level: str = None,
) -> None:
    """初始化并配置全局日志记录器。

    Args:
        log_dir: 日志保存目录，默认从配置文件读取。
        rotation: 日志轮转条件（大小或时间），默认从配置文件读取。
        retention: 日志保留时长，默认从配置文件读取。
        console_level: 控制台输出级别，默认从配置文件读取。
        file_level: 文件输出级别，默认从配置文件读取。
    """
    log_cfg = config.logger

    log_dir = log_dir or log_cfg.path
    rotation = rotation or log_cfg.rotation
    retention = retention or log_cfg.retention
    log_level = log_cfg.level
    console_enabled = log_cfg.console

    console_level = console_level or log_level
    file_level = file_level or log_level

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 移除 Loguru 默认的处理器，避免重复输出
    logger.remove()

    # 1. 控制台处理器（带颜色与格式）
    if console_enabled:
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            level=console_level,
            colorize=True,
            enqueue=True,
        )

    # 2. 全量日志文件处理器
    logger.add(
        log_path / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level=file_level,
        rotation=rotation,
        retention=retention,
        compression=log_cfg.compression,
        encoding="utf-8",
        enqueue=True,
    )

    # 3. 错误日志专属文件处理器
    logger.add(
        log_path / "error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation=rotation,
        retention=retention,
        compression=log_cfg.compression,
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )


# ---------------------------------------------------------------------------
# 便捷包装方法（向下兼容）
# 使用 opt(depth=1) 使 loguru 忽略当前包装层，正确显示业务代码的文件名与行号。
# ---------------------------------------------------------------------------

def debug(message: str, *args: Any, **kwargs: Any) -> None:
    logger.opt(depth=1).debug(message, *args, **kwargs)


def info(message: str, *args: Any, **kwargs: Any) -> None:
    logger.opt(depth=1).info(message, *args, **kwargs)


def warning(message: str, *args: Any, **kwargs: Any) -> None:
    logger.opt(depth=1).warning(message, *args, **kwargs)


def error(message: str, *args: Any, **kwargs: Any) -> None:
    logger.opt(depth=1).error(message, *args, **kwargs)


def critical(message: str, *args: Any, **kwargs: Any) -> None:
    logger.opt(depth=1).critical(message, *args, **kwargs)


# 模块被导入时自动执行基础初始化
init_logger()
