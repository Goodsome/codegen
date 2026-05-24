from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstExprStmt(AstStmt):
    """Represents an ast.Expr node (expression statement)."""

    value: AstExpr
