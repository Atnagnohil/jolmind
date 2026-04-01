from __future__ import annotations
from typing import Dict
from pydantic import BaseModel
import yaml
from pathlib import Path


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


# 应用总配置
class AppConfig(BaseModel):
    llm: LLMConfig
    logger: LoggerConfig


def load_config(path: str = "config.yaml") -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return AppConfig.model_validate(raw)

config = load_config()