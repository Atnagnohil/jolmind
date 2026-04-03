from sqlalchemy.orm import Session

from src.config import config
from src.db.crud import get_session, update_session
from src.providers.llm.registry import registry

_NAMING_PROMPT = """根据以下用户消息，为这次对话生成一个简洁的标题。
要求：
- 不超过 15 个字
- 概括对话主题
- 不要加引号或标点符号
- 直接输出标题，不要有任何解释

用户消息：{message}"""


async def generate_session_name(message: str) -> str:
    """根据用户首条消息生成会话标题。"""
    try:
        provider = registry.create(config.llm.default)
        llm = provider.get_model()
        result = await llm.ainvoke(_NAMING_PROMPT.format(message=message[:200]))
        name = result.content.strip()[:64]
        return name if name else "新会话"
    except Exception:
        return "新会话"


async def auto_name_session(db: Session, session_id: str, message: str) -> None:
    """
    若会话仍为默认名称，在后台异步生成并更新标题。
    使用 asyncio.create_task 调用，不阻塞主流程。
    """
    session = get_session(db, session_id)
    if session and session.session_name == "新会话":
        name = await generate_session_name(message)
        update_session(db, session_id, session_name=name)
