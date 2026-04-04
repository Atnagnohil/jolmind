from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from src.config import config
from src.providers.tts import registry

router = APIRouter(prefix="/tts", tags=["语音合成"])


class TTSRequest(BaseModel):
    text: str = Field(..., description="待合成的文本")
    provider: str = Field("", description="TTS 提供商名称，留空使用默认")


@router.post("", summary="文本转语音（完整返回）")
async def tts(body: TTSRequest):
    provider_name = body.provider or config.tts.default
    if not provider_name:
        raise HTTPException(status_code=400, detail="未指定 TTS provider 且未配置默认值")
    try:
        provider = registry.create(provider_name)
        print(1)
        audio = await provider.synthesize(body.text)
        print(2)
        return Response(content=audio, media_type="audio/mpeg")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream", summary="文本转语音（流式返回）")
async def tts_stream(body: TTSRequest):
    provider_name = body.provider or config.tts.default
    if not provider_name:
        raise HTTPException(status_code=400, detail="未指定 TTS provider 且未配置默认值")
    try:
        provider = registry.create(provider_name)

        async def generate():
            async for chunk in provider.synthesize_stream(body.text):
                yield chunk

        return StreamingResponse(generate(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
