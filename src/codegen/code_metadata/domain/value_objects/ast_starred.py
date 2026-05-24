import ast
from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstStarred(AstExpr):
    """Represents an ast.Starred node (e.g., *args)."""

    value: AstExpr
    ctx: ast.expr_context | None = None
