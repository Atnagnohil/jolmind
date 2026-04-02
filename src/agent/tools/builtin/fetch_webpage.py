from bs4 import BeautifulSoup

from src.agent.tools import register_tool
from src.utils.http_client import http

# 单次抓取返回的最大字符数，避免超出 context window
_MAX_CHARS = 4000


@register_tool
def fetch_webpage(url: str) -> str:
    """抓取指定网页的正文内容。

    Args:
        url: 要抓取的网页 URL。
    """
    try:
        response = http.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Jolmind/1.0)"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 移除无用标签
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # 优先取 <article> / <main>，否则取 <body>
        main = soup.find("article") or soup.find("main") or soup.body
        text = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)

        # 合并多余空行
        lines = [line for line in text.splitlines() if line.strip()]
        content = "\n".join(lines)

        if len(content) > _MAX_CHARS:
            content = content[:_MAX_CHARS] + f"\n\n... （内容已截断，共 {len(content)} 字符）"

        return content or "页面内容为空。"

    except Exception as e:
        return f"抓取失败：{e}"
