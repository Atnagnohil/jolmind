from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agent.memory import SaverFactory
from src.api.routers import chat, health, messages, providers, sessions, tool_call_logs, users
from src.config import config
from src.utils.langsmith import init_langsmith
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动初始化 / 关闭释放资源。"""
    init_langsmith()
    await SaverFactory.open()
    logger.info("Jolmind 启动")
    yield
    await SaverFactory.close()
    logger.info("Jolmind 已关闭")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Jolmind API",
        description="Jolmind 私人助手接口",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.web.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(sessions.router)
    app.include_router(messages.router)
    app.include_router(tool_call_logs.router)
    app.include_router(providers.router)
    app.include_router(chat.router)

    return app
