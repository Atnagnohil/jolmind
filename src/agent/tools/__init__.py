from src.agent.tools.base import (
    TOOL_REGISTRY,
    disable_tool,
    enable_tool,
    get_enabled_tools,
    register_tool,
)

# 导入内置工具，触发 @register_tool 自动注册
from src.agent.tools.builtin import calculator, time_tool  # noqa: F401

__all__ = [
    "register_tool",
    "get_enabled_tools",
    "enable_tool",
    "disable_tool",
    "TOOL_REGISTRY",
]
