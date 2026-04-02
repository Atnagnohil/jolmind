from tavily import TavilyClient

from src.agent.tools import register_tool
from src.config import config


@register_tool
def web_search(query: str, num_results: int = 5) -> str:
    """搜索网络，返回与查询相关的网页标题、链接和摘要。

    Args:
        query: 搜索关键词。
        num_results: 返回结果数量，默认 5 条。
    """
    api_key = config.tavily.api_key
    if not api_key or api_key == "your-tavily-api-key":
        return "错误：请在 config.yaml 中配置 tavily.api_key。"

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=num_results)

        results = response.get("results", [])
        if not results:
            return "未找到相关结果。"

        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r.get('title', '无标题')}")
            lines.append(f"   链接：{r.get('url', '')}")
            if r.get("content"):
                lines.append(f"   摘要：{r['content'][:400]}")
        return "\n".join(lines)
    except Exception as e:
        return f"搜索失败：{e}"
