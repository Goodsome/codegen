from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstAnnAssign(AstStmt):
    """Represents an ast.AnnAssign node (annotated assignment)."""

    target: AstExpr
    annotation: AstExpr
    value: AstExpr | None = None
    simple: int = 0
