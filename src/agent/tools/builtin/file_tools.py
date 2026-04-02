from pathlib import Path

from src.agent.tools import register_tool
from src.config import config

# 从配置文件读取工作目录
_WORKSPACE = Path(config.files.workspace).expanduser().resolve()
_WORKSPACE.mkdir(parents=True, exist_ok=True)

# 单次读取最大字符数
_MAX_READ_CHARS = 8000


def _safe_path(filename: str) -> Path:
    """将文件名解析为安全路径，禁止路径穿越。"""
    path = (_WORKSPACE / filename).resolve()
    if not path.is_relative_to(_WORKSPACE.resolve()):
        raise PermissionError(f"禁止访问工作目录以外的路径：{filename}")
    return path


@register_tool
def read_file(filename: str) -> str:
    """读取文件内容。只能访问用户工作目录内的文件。

    Args:
        filename: 文件名或相对路径，如 'notes.txt' 或 'docs/report.md'。
    """
    try:
        path = _safe_path(filename)
        if not path.exists():
            return f"文件不存在：{filename}"
        if not path.is_file():
            return f"路径不是文件：{filename}"

        content = path.read_text(encoding="utf-8")
        if len(content) > _MAX_READ_CHARS:
            content = content[:_MAX_READ_CHARS] + f"\n\n... （内容已截断，共 {len(content)} 字符）"
        return content or "（文件内容为空）"
    except PermissionError as e:
        return f"权限错误：{e}"
    except Exception as e:
        return f"读取失败：{e}"


@register_tool
def write_file(filename: str, content: str, append: bool = False) -> str:
    """将内容写入文件。只能写入用户工作目录内的文件。

    Args:
        filename: 文件名或相对路径，如 'notes.txt' 或 'docs/report.md'。
        content: 要写入的文本内容。
        append: 为 True 时追加到文件末尾，默认覆盖写入。
    """
    try:
        path = _safe_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        path.open(mode, encoding="utf-8").write(content)

        action = "追加" if append else "写入"
        return f"已{action} {len(content)} 个字符到 {filename}"
    except PermissionError as e:
        return f"权限错误：{e}"
    except Exception as e:
        return f"写入失败：{e}"


@register_tool
def list_files(directory: str = "") -> str:
    """列出工作目录下的文件和文件夹。

    Args:
        directory: 子目录路径，默认列出根工作目录。
    """
    try:
        path = _safe_path(directory) if directory else _WORKSPACE
        if not path.exists():
            return f"目录不存在：{directory}"
        if not path.is_dir():
            return f"路径不是目录：{directory}"

        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        if not entries:
            return "（目录为空）"

        lines = []
        for entry in entries:
            prefix = "文件" if entry.is_file() else "文件夹"
            size = f"  {entry.stat().st_size} 字节" if entry.is_file() else ""
            lines.append(f"{prefix} {entry.name}{size}")
        return "\n".join(lines)
    except PermissionError as e:
        return f"权限错误：{e}"
    except Exception as e:
        return f"列出失败：{e}"
