import ast
import operator
from typing import Union

from src.agent.tools import register_tool

# 允许的运算符白名单，避免 eval 安全风险
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不支持的表达式: {ast.dump(node)}")


@register_tool
def calculator(expression: str) -> str:
    """计算数学表达式，支持 + - * / // % ** 运算。

    Args:
        expression: 数学表达式字符串，例如 "2 ** 10" 或 "(3 + 5) * 2"。
    """
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree.body)
        # 整数结果去掉小数点
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
    except ZeroDivisionError:
        return "错误：除数不能为零"
    except Exception as e:
        return f"错误：{e}"
