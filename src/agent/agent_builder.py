from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from src.agent.memory import SaverFactory
from src.agent.prompt import get_agent_prompt, get_think_prompt
from src.agent.tools import get_enabled_tools
from src.providers.llm.registry import registry


def _parse_model(model: str) -> tuple[str, str | None]:
    parts = model.split("/", 1)
    return parts[0], parts[1] if len(parts) > 1 else None


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    thinking: str  # 思考节点的输出，传递给执行节点作为上下文


def build_agent(model: str, session_id: str, enable_think: bool = True):
    """
    构建 CoT Agent。

    Args:
        model: 模型标识，格式为 'provider_name' 或 'provider_name/model_name'。
        session_id: 会话 ID，用于 checkpoint 隔离。
        enable_think: 是否启用 think 节点，默认开启。
    """
    provider_name, model_name = _parse_model(model)
    llm = registry.create(provider_name).get_model(model_name)

    tools = get_enabled_tools()
    llm_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    think_prompt = get_think_prompt()
    act_prompt = get_agent_prompt()

    # ── 思考节点 ──────────────────────────────────────────────
    async def think_node(state: AgentState) -> dict:
        """分析用户意图，输出思考内容，不调工具。"""
        sys_msg = SystemMessage(content=think_prompt)
        response = await llm.ainvoke([sys_msg] + state["messages"])
        return {"thinking": response.content}

    # ── 执行节点 ──────────────────────────────────────────────
    async def act_node(state: AgentState) -> dict:
        """携带思考结果，执行 ReAct 循环给出最终回复。"""
        # enable_think=False 时忽略 checkpoint 中残留的旧 thinking
        thinking = state.get("thinking", "") if enable_think else ""
        sys_content = act_prompt
        if thinking:
            sys_content += f"\n\n## 前期分析结论\n{thinking}"
        sys_msg = SystemMessage(content=sys_content)
        response = await llm_with_tools.ainvoke([sys_msg] + state["messages"])
        return {"messages": [response], "thinking": thinking}

    # ── 工具调用后是否继续循环 ────────────────────────────────
    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return END

    # ── 构建 Graph ────────────────────────────────────────────
    graph = StateGraph(AgentState)
    graph.add_node("act", act_node)
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("act", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "act")

    if enable_think:
        graph.add_node("think", think_node)
        graph.set_entry_point("think")
        graph.add_edge("think", "act")
    else:
        graph.set_entry_point("act")

    return graph.compile(checkpointer=SaverFactory.get_saver())
