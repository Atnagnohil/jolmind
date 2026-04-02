from typing import Callable

from langchain_core.tools import BaseTool, tool

# 全局工具注册表，key 为工具名称
TOOL_REGISTRY: dict[str, BaseTool] = {}

# 禁用的工具名称集合
_DISABLED_TOOLS: set[str] = set()


def register_tool(func: Callable) -> BaseTool:
    """
    工具注册装饰器，自动将函数包装为 LangChain Tool 并注册到 TOOL_REGISTRY。

    用法：
        @register_tool
        def search_web(query: str) -> str:
            '''搜索网络'''
            ...
    """
    wrapped: BaseTool = tool(func)
    TOOL_REGISTRY[wrapped.name] = wrapped
    return wrapped


def disable_tool(name: str) -> None:
    """禁用指定工具，使其不出现在 get_enabled_tools() 结果中。"""
    _DISABLED_TOOLS.add(name)


def enable_tool(name: str) -> None:
    """重新启用指定工具。"""
    _DISABLED_TOOLS.discard(name)


def get_enabled_tools() -> list[BaseTool]:
    """返回所有已注册且未被禁用的工具列表。"""
    return [t for name, t in TOOL_REGISTRY.items() if name not in _DISABLED_TOOLS]
