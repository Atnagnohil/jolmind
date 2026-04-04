from src.providers.tts.registry import registry
from src.providers.tts.xfyun_provider import XfyunTTSProvider

registry.register("xfyun", XfyunTTSProvider)

__all__ = ["registry"]
