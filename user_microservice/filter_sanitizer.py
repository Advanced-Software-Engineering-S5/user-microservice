import ast
import astor
from datetime import datetime

whitelist = [
    ast.Expression, ast.Compare, ast.Num, ast.Lt, ast.Gt, ast.Eq, ast.GtE, ast.LtE, ast.NotEq, ast.Tuple, ast.Load,
    ast.Name, ast.Attribute, ast.Constant, ast.Str
]


def sanitize_filter(stmt: str) -> str:
    class RewriteDatetime(ast.NodeTransformer):
        def visit_Str(self, node):
            try:
                parse = datetime.fromisoformat(node.s)
                return ast.Call(func=ast.Attribute(value=ast.Name(id='datetime', ctx=ast.Load()),
                                                   attr='fromisoformat',
                                                   ctx=ast.Load()),
                                args=[ast.Constant(value=node.s, kind=None)],
                                keywords=[])
            except (TypeError, ValueError):
                return node

    try:
        tree = ast.parse(stmt, mode='eval')
        for node in ast.walk(tree):
            if not type(node) in whitelist:
                return ""

        return astor.to_source(RewriteDatetime().visit(tree))
    except SyntaxError:
        return ""
