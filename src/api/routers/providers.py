from fastapi import APIRouter, HTTPException

from src.api.schemas import Response
from src.config import config
from src.providers.llm.registry import registry

router = APIRouter(prefix="/providers", tags=["模型提供商"])


@router.get("", response_model=Response[list[dict]])
def list_providers():
    """列出所有已配置的提供商"""
    result = [
        {
            "name": name,
            "type": cfg.type,
            "default_model": cfg.default,
        }
        for name, cfg in config.llm.providers.items()
    ]
    return Response.ok(result)


@router.get("/{provider_name}/models", response_model=Response[list[str]])
async def list_models(provider_name: str):
    """获取指定提供商支持的模型列表"""
    if provider_name not in config.llm.providers:
        raise HTTPException(status_code=404, detail=f"提供商 '{provider_name}' 不存在")
    try:
        provider = registry.create(provider_name)
        models = await provider.list_models()
        return Response.ok(models)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"获取模型列表失败：{e}")
