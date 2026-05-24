from dataclasses import dataclass
import ast

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstAugAssign(AstStmt):
    """Represents an ast.AugAssign node (e.g., x += 1)."""

    target: AstExpr
    op: ast.operator
    value: AstExpr
