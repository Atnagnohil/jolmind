from abc import ABC, abstractmethod
from typing import AsyncIterator


class TTSProvider(ABC):
    """TTS 提供者抽象接口"""

    @abstractmethod
    async def synthesize(self, text: str, **kwargs) -> bytes:
        """将文本合成为音频，返回完整音频字节。"""

    @abstractmethod
    async def synthesize_stream(self, text: str, **kwargs) -> AsyncIterator[bytes]:
        """将文本合成为音频，流式返回音频块。"""
