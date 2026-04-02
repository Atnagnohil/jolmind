import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.agent.agent_builder import build_agent
from src.agent.persistence import collect_message_ids, persist_messages
from src.api.deps import get_db
from src.api.schemas import Response

router = APIRouter(prefix="/chat", tags=["对话"])


class ChatRequest(BaseModel):
    user_id: int = Field(..., description="用户 ID")
    session_id: str = Field(..., description="会话 ID，对应 LangGraph thread_id")
    message: str = Field(..., description="用户消息")
    model: str = Field(..., description="模型标识，格式 provider 或 provider/model")


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@router.post("", response_model=Response[ChatResponse])
async def chat(body: ChatRequest, db: Session = Depends(get_db)):
    """非流式对话，自动持久化消息和工具调用日志"""
    try:
        start = time.monotonic()
        agent = build_agent(model=body.model, session_id=body.session_id)
        cfg = {"configurable": {"thread_id": body.session_id}}

        prior = await agent.aget_state(cfg)
        existing_ids = collect_message_ids(prior.values.get("messages", []))

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": body.message}]},
            config=cfg,
        )
        persist_messages(db, body.user_id, body.session_id, result["messages"], start, existing_ids)
        reply = result["messages"][-1].content
        return Response.ok(ChatResponse(session_id=body.session_id, reply=reply))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(body: ChatRequest, db: Session = Depends(get_db)):
    """流式对话，返回 text/event-stream，结束后持久化消息"""

    async def generate() -> AsyncGenerator[str, None]:
        try:
            start = time.monotonic()
            agent = build_agent(model=body.model, session_id=body.session_id)
            cfg = {"configurable": {"thread_id": body.session_id}}

            prior = await agent.aget_state(cfg)
            existing_ids = collect_message_ids(prior.values.get("messages", []))

            async for chunk in agent.astream(
                    {"messages": [{"role": "user", "content": body.message}]},
                    config=cfg,
                    stream_mode="messages",
            ):
                msg, metadata = chunk
                yield f"data: {msg.content}\n\n"

            # 流结束后从 checkpoint 拿完整消息列表再持久化
            final_state = await agent.aget_state(cfg)
            persist_messages(db, body.user_id, body.session_id, final_state.values.get("messages", []), start,
                             existing_ids)
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
