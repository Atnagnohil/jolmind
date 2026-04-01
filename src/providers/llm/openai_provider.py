from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.config import config
from src.providers.llm.base import LLMProvider
from src.utils import http


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider 实现"""

    MODELS_URI = "/models"

    def __init__(self, provider_name: str | None = None):
        original_name = provider_name or config.llm.default
        self.config = config.llm.providers[original_name]

    async def list_models(self) -> list[str]:
        """获取支持的模型列表"""
        response = await http.async_get(
            self.config.base_url + self.MODELS_URI,
            headers={"Authorization": f"Bearer {self.config.api_key}"},
        )
        return [model.id for model in response.json().data]

    def get_model(self, model: str | None = None, max_tokens: int | None = None) -> BaseChatModel:
        """获取模型"""
        return ChatOpenAI(
            model=model or self.config.default,
            base_url=self.config.base_url,
            api_key=SecretStr(self.config.api_key),
            max_tokens=max_tokens,
        )
