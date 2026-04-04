import asyncio
import base64
import hashlib
import hmac
import json
import ssl
from datetime import datetime
from time import mktime
from typing import AsyncIterator
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websocket

from src.config import config
from src.providers.tts.base import TTSProvider


class XfyunTTSProvider(TTSProvider):
    """讯飞 TTS provider（WebSocket 接口）"""

    WS_URL = "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6"

    def __init__(self, provider_name: str):
        cfg = config.tts.providers[provider_name]
        self.app_id = cfg.app_id
        self.api_key = cfg.api_key
        self.api_secret = cfg.api_secret
        self.vcn = cfg.extra.get("vcn", "x4_lingxiaoxuan_oral")
        self.sample_rate = int(cfg.extra.get("sample_rate", 24000))
        self.encoding = cfg.extra.get("encoding", "lame")

    def _build_auth_url(self) -> str:
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        from urllib.parse import urlparse
        parsed = urlparse(self.WS_URL)
        host = parsed.netloc
        path = parsed.path
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"),
                signature_origin.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        authorization = base64.b64encode(
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'.encode("utf-8")
        ).decode("utf-8")
        return self.WS_URL + "?" + urlencode({"host": host, "date": date, "authorization": authorization})

    def _build_payload(self, text: str) -> str:
        return json.dumps({
            "header": {"app_id": self.app_id, "status": 2},
            "parameter": {
                "tts": {
                    "vcn": self.vcn,
                    "volume": 50,
                    "speed": 50,
                    "pitch": 50,
                    "audio": {
                        "encoding": self.encoding,
                        "sample_rate": self.sample_rate,
                        "channels": 1,
                        "bit_depth": 16,
                        "frame_size": 0,
                    },
                }
            },
            "payload": {
                "text": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 2,
                    "seq": 0,
                    "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
                }
            },
        })

    async def synthesize(self, text: str, **kwargs) -> bytes:
        """同步合成，返回完整音频字节。"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._synthesize_sync, text)

    def _synthesize_sync(self, text: str) -> bytes:
        audio_chunks: list[bytes] = []
        done_event = asyncio.Event() if False else None  # 同步用 threading.Event
        import threading
        done = threading.Event()
        error: list[Exception] = []

        payload = self._build_payload(text)

        def on_open(ws):
            ws.send(payload)

        def on_message(ws, message):
            try:
                msg = json.loads(message)
                if msg["header"]["code"] != 0:
                    error.append(RuntimeError(f"讯飞 TTS 错误: {msg}"))
                    ws.close()
                    return
                if "payload" not in msg:
                    return
                audio_b64 = msg["payload"]["audio"]["audio"]
                audio_chunks.append(base64.b64decode(audio_b64))
                if msg["payload"]["audio"]["status"] == 2:
                    ws.close()
            except Exception as e:
                error.append(e)
                ws.close()

        def on_error(ws, err):
            error.append(RuntimeError(str(err)))

        def on_close(ws, *args):
            done.set()

        ws = websocket.WebSocketApp(
            self._build_auth_url(),
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        done.wait(timeout=30)

        if error:
            raise error[0]
        return b"".join(audio_chunks)

    async def synthesize_stream(self, text: str, **kwargs) -> AsyncIterator[bytes]:
        """流式合成，逐块 yield 音频数据。"""
        queue: asyncio.Queue[bytes | None] = asyncio.Queue()
        loop = asyncio.get_event_loop()
        payload = self._build_payload(text)

        def on_open(ws):
            ws.send(payload)

        def on_message(ws, message):
            try:
                msg = json.loads(message)
                if msg["header"]["code"] != 0:
                    loop.call_soon_threadsafe(queue.put_nowait, None)
                    ws.close()
                    return
                if "payload" not in msg:
                    return
                audio_b64 = msg["payload"]["audio"]["audio"]
                chunk = base64.b64decode(audio_b64)
                loop.call_soon_threadsafe(queue.put_nowait, chunk)
                if msg["payload"]["audio"]["status"] == 2:
                    loop.call_soon_threadsafe(queue.put_nowait, None)
                    ws.close()
            except Exception:
                loop.call_soon_threadsafe(queue.put_nowait, None)
                ws.close()

        def on_error(ws, err):
            loop.call_soon_threadsafe(queue.put_nowait, None)

        def on_close(ws, *args):
            loop.call_soon_threadsafe(queue.put_nowait, None)

        def run_ws():
            ws = websocket.WebSocketApp(
                self._build_auth_url(),
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        import threading
        threading.Thread(target=run_ws, daemon=True).start()

        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk
