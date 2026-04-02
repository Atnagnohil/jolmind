from src.agent.agent_builder import build_agent
from src.agent.memory import SaverFactory
from src.utils.langsmith import init_langsmith
from src.utils.logger import logger


def main():
    init_langsmith()
    SaverFactory.open()
    logger.info("Jolmind 启动")
    try:
        session_id = "user-001"
        agent = build_agent(model="34ku/gpt-4o-mini", session_id=session_id)
        config = {"configurable": {"thread_id": session_id}}

        # 多轮对话示例
        while True:
            user_input = input("你：").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "退出"):
                break

            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )
            reply = result["messages"][-1].content
            print(f"Jolmind：{reply}\n")

    finally:
        SaverFactory.close()
        logger.info("Jolmind 已关闭")


if __name__ == "__main__":
    main()
