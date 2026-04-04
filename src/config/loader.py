from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml
from pydantic import BaseModel


# 单个提供商配置
class LLMProviderConfig(BaseModel):
    # 提供商类型
    type: str
    # 提供商base_url
    base_url: str
    # 提供商api_key
    api_key: str
    # 提供商默认选中的模型
    default: str


# LLM 整体配置
class LLMConfig(BaseModel):
    # 默认使用的提供商名称
    default: str
    # 所有提供商配置，key 为提供商名称
    providers: Dict[str, LLMProviderConfig]


# 日志配置
class LoggerConfig(BaseModel):
    path: str
    level: str
    rotation: str
    retention: str
    compression: str
    console: bool


# 记忆配置
class MemoryConfig(BaseModel):
    # sqlite 数据库路径
    sqlite_path: str


# LangSmith 追踪配置
class LangSmithConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    project: str = "jolmind"
    endpoint: str = "https://api.smith.langchain.com"


# 文件工具配置
class FilesConfig(BaseModel):
    workspace: str = "~/jolmind_files"


# Tavily 搜索配置
class TavilyConfig(BaseModel):
    api_key: str = ""


# 单个 TTS 提供商配置
class TTSProviderConfig(BaseModel):
    type: str
    app_id: str = ""
    api_key: str = ""
    api_secret: str = ""
    extra: Dict[str, str] = {}


# TTS 整体配置
class TTSConfig(BaseModel):
    default: str = ""
    providers: Dict[str, TTSProviderConfig] = {}


# Web 服务配置
class WebConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]


# 数据库配置
class DbConfig(BaseModel):
    url: str = "mysql+pymysql://root:password@localhost:3306/jolmind?charset=utf8mb4"


# 应用总配置
class AppConfig(BaseModel):
    llm: LLMConfig
    logger: LoggerConfig
    memory: MemoryConfig
    files: FilesConfig = FilesConfig()
    tavily: TavilyConfig = TavilyConfig()
    tts: TTSConfig = TTSConfig()
    web: WebConfig = WebConfig()
    db: DbConfig = DbConfig()
    langsmith: LangSmithConfig = LangSmithConfig()


def load_config(path: str = "config.yaml") -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return AppConfig.model_validate(raw)


config = load_config()
