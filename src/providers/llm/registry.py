from typing import Dict, Optional, Type

from src.config import config
from src.providers.llm.base import LLMProvider


class LLMProviderRegistry:
    """
    LLM 提供者注册表。

    将提供者类型映射到其实现类。
    具有相同类型的多个提供者共享同一个类。
    """

    _instance: Optional["LLMProviderRegistry"] = None
    _providers: Dict[str, Type[LLMProvider]]

    def __new__(cls) -> "LLMProviderRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_providers"):
            self._providers = {}

    def register(self, provider_type: str, provider_class: Type[LLMProvider]) -> None:
        """为特定类型注册提供者类。"""
        self._providers[provider_type] = provider_class

    def get(self, provider_type: str) -> Type[LLMProvider]:
        """通过类型检索提供者类，未找到则抛出 KeyError。"""
        if provider_type not in self._providers:
            raise KeyError(f"Provider type '{provider_type}' not found in registry")
        return self._providers[provider_type]

    def create(self, provider_name: str) -> LLMProvider:
        """
        从配置创建提供者实例。

        Args:
            provider_name: config.yaml 中的提供者名称（例如 "siliconflow"、"nvidia"）

        Returns:
            实例化的提供者对象
        """
        providers = config.llm.providers
        if provider_name not in providers:
            raise ValueError(f"Provider '{provider_name}' not found in configuration")

        provider_type = providers[provider_name].type
        provider_class = self.get(provider_type)
        return provider_class(provider_name=provider_name)

    def list_types(self) -> list[str]:
        """列出所有已注册的提供者类型。"""
        return list(self._providers.keys())

    def is_registered(self, provider_type: str) -> bool:
        """检查提供者类型是否已注册。"""
        return provider_type in self._providers


registry = LLMProviderRegistry()
