import asyncio
import json
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.agent.agent_builder import build_agent
from src.agent.naming import auto_name_session
from src.agent.persistence import collect_message_ids, persist_messages
from src.api.deps import get_db
from src.api.schemas import Response
from src.db.crud import update_session

router = APIRouter(prefix="/chat", tags=["对话"])


class ChatRequest(BaseModel):
    user_id: int = Field(..., description="用户 ID")
    session_id: str = Field(..., description="会话 ID，对应 LangGraph thread_id")
    message: str = Field(..., description="用户消息")
    model: str = Field(..., description="模型标识，格式 provider 或 provider/model")
    enable_think: bool = Field(True, description="是否启用 think 模式，开启后会先进行推理再回复")


class ChatResponse(BaseModel):
    session_id: str
    reply: str


def _sse(type_: str, content: str) -> str:
    return f"data: {json.dumps({'type': type_, 'content': content}, ensure_ascii=False)}\n\n"


@router.post("", response_model=Response[ChatResponse])
async def chat(body: ChatRequest, db: Session = Depends(get_db)):
    """非流式对话，自动持久化消息和工具调用日志"""
    try:
        start = time.monotonic()
        agent = build_agent(model=body.model, session_id=body.session_id, enable_think=body.enable_think)
        cfg = {"configurable": {"thread_id": body.session_id}}

        prior = await agent.aget_state(cfg)
        existing_ids = collect_message_ids(prior.values.get("messages", []))

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": body.message}]},
            config=cfg,
        )
        persist_messages(db, body.user_id, body.session_id, result["messages"], start, existing_ids,
                         thinking=result.get("thinking", ""))
        asyncio.create_task(auto_name_session(db, body.session_id, body.message))
        reply = result["messages"][-1].content
        return Response.ok(ChatResponse(session_id=body.session_id, reply=reply))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(body: ChatRequest, db: Session = Depends(get_db)):
    """
    流式对话，返回 text/event-stream。
    事件格式：
      {"type": "thinking", "content": "..."}  — think 节点推理过程
      {"type": "text",     "content": "..."}  — act 节点最终回复
      {"type": "done"}                         — 结束
      {"type": "error",    "content": "..."}  — 异常
    """

    async def generate() -> AsyncGenerator[str, None]:
        try:
            start = time.monotonic()
            agent = build_agent(model=body.model, session_id=body.session_id, enable_think=body.enable_think)
            cfg = {"configurable": {"thread_id": body.session_id}}

            prior = await agent.aget_state(cfg)
            existing_ids = collect_message_ids(prior.values.get("messages", []))

            async for event in agent.astream_events(
                {"messages": [{"role": "user", "content": body.message}]},
                config=cfg,
                version="v2",
            ):
                kind = event["event"]
                node = event.get("metadata", {}).get("langgraph_node", "")

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    content = chunk.content
                    if not content:
                        continue
                    if node == "think":
                        yield _sse("thinking", content)
                    elif node == "act":
                        yield _sse("text", content)

            # 流结束后持久化
            final_state = await agent.aget_state(cfg)
            persist_messages(
                db, body.user_id, body.session_id,
                final_state.values.get("messages", []),
                start, existing_ids,
                thinking=final_state.values.get("thinking", ""),
            )
            asyncio.create_task(auto_name_session(db, body.session_id, body.message))
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield _sse("error", str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")
