from langchain.agents import create_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.agent.memory import SaverFactory
from src.agent.prompt import get_agent_prompt
from src.agent.tools import get_enabled_tools
from src.config import config
from src.providers.llm.registry import registry


def _parse_model(model: str) -> tuple[str, str | None]:
    """解析 'provider/model' 格式，model 部分可选。"""
    parts = model.split("/", 1)
    return parts[0], parts[1] if len(parts) > 1 else None


def build_agent(model: str, session_id: str):
    """
    构建 ReAct Agent。

    Args:
        model: 模型标识，格式为 'provider_name' 或 'provider_name/model_name'。
        session_id: 会话 ID，用于 checkpoint 隔离。
    """
    provider_name, model_name = _parse_model(model)
    llm = registry.create(provider_name).get_model(model_name)

    tools = get_enabled_tools()
    prompt = get_agent_prompt()

    return create_agent(
        model=llm.bind_tools(tools),
        tools=tools,
        system_prompt=prompt,
        checkpointer=SaverFactory.get_saver(),
    )


async def build_agent_with_async(model: str, session_id: str):
    """
    构建 ReAct Agent, 异步checkpoint。

    Args:
        model: 模型标识，格式为 'provider_name' 或 'provider_name/model_name'。
        session_id: 会话 ID，用于 checkpoint 隔离。
    """
    provider_name, model_name = _parse_model(model)
    llm = registry.create(provider_name).get_model(model_name)

    tools = get_enabled_tools()
    prompt = get_agent_prompt()

    sqlite_path = config.memory.sqlite_path
    async with AsyncSqliteSaver.from_conn_string(sqlite_path) as checkpointer:
        return create_agent(
            model=llm.bind_tools(tools),
            tools=tools,
            system_prompt=prompt,
            checkpointer=checkpointer,
        )
