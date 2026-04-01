"""BaseLLM Provider接口"""

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel


class LLMProvider(ABC):
    """LLM提供者接口"""

    @abstractmethod
    async def list_models(self) -> list[str]:
        pass

    @abstractmethod
    def get_model(self, model: str | None = None, max_tokens: int | None = None) -> BaseChatModel:
        pass

    async def supports_model(self, model: str) -> bool:
        return model in await self.list_models()
