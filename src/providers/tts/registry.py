from typing import Dict, Optional, Type

from src.providers.tts.base import TTSProvider


class TTSProviderRegistry:
    _instance: Optional["TTSProviderRegistry"] = None
    _providers: Dict[str, Type[TTSProvider]]

    def __new__(cls) -> "TTSProviderRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_providers"):
            self._providers = {}

    def register(self, provider_type: str, provider_class: Type[TTSProvider]) -> None:
        self._providers[provider_type] = provider_class

    def create(self, provider_name: str) -> TTSProvider:
        """
        从配置创建 TTS 提供者实例。

        Args:
            provider_name: config.yaml tts.providers 中的 key
        """
        from src.config import config

        providers = config.tts.providers
        if provider_name not in providers:
            raise ValueError(f"TTS provider '{provider_name}' not found in configuration")

        provider_type = providers[provider_name].type
        if provider_type not in self._providers:
            raise KeyError(f"TTS provider type '{provider_type}' is not registered")

        return self._providers[provider_type](provider_name=provider_name)

    def list_types(self) -> list[str]:
        return list(self._providers.keys())


registry = TTSProviderRegistry()
