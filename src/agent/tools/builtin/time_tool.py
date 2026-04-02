from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.agent.tools import register_tool


@register_tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前日期和时间。

    Args:
        timezone: 时区名称，默认为 Asia/Shanghai（北京时间）。
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
        return now.strftime("%Y年%m月%d日 %H:%M:%S %Z")
    except ZoneInfoNotFoundError:
        return f"错误：未知时区 '{timezone}'，请使用 IANA 时区名称，如 Asia/Shanghai、America/New_York。"
