"""
calculator_engine.py
---------------------
Core calculator logic: safely evaluates math expressions like "5 + 3 * 2".

Why not just use Python's built-in eval()?
eval() runs ANY Python code, so a user could type something malicious like
"__import__('os').system('rm -rf /')" and it would actually execute.

Instead, we parse the expression into an Abstract Syntax Tree (AST) and only
walk through a whitelisted set of safe operations. This is a common pattern
for building safe expression evaluators.
"""

import ast
import math
import operator

# Map AST operator nodes to the real Python functions that perform them
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNARY_OPERATORS = {
    ast.USub: operator.neg,  # e.g. the "-" in "-5"
    ast.UAdd: operator.pos,
}

# Function calls the calculator understands, e.g. sqrt(16)
ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "log": math.log,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "factorial": math.factorial,
    "round": round,
}


class CalculatorError(Exception):
    """Raised whenever an expression can't be safely evaluated."""
    pass


def _eval_node(node):
    """Recursively evaluate one node of the parsed expression tree."""

    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise CalculatorError("Only numbers are allowed")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in BINARY_OPERATORS:
            raise CalculatorError(f"'{op_type.__name__}' is not a supported operator")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        try:
            return BINARY_OPERATORS[op_type](left, right)
        except ZeroDivisionError:
            raise CalculatorError("Cannot divide by zero")

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in UNARY_OPERATORS:
            raise CalculatorError(f"'{op_type.__name__}' is not a supported operator")
        return UNARY_OPERATORS[op_type](_eval_node(node.operand))

    if isinstance(node, ast.Call):
        func_name = node.func.id if isinstance(node.func, ast.Name) else None
        if func_name not in ALLOWED_FUNCTIONS:
            raise CalculatorError(f"Unknown function '{func_name}'")
        args = [_eval_node(arg) for arg in node.args]
        try:
            return ALLOWED_FUNCTIONS[func_name](*args)
        except (ValueError, TypeError) as exc:
            raise CalculatorError(str(exc))

    raise CalculatorError("Unsupported expression")


def evaluate(expression: str):
    """Take a math expression string like '5 + 3 * 2' and return the result."""
    expression = (expression or "").strip()
    if not expression:
        raise CalculatorError("Empty expression")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise CalculatorError("That doesn't look like a valid expression")

    result = _eval_node(tree)

    # Return whole numbers as ints (e.g. 4.0 -> 4) for a cleaner display
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return result
