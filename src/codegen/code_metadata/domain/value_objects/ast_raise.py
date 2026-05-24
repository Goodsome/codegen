from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstRaise(AstStmt):
    """Represents an ast.Raise node."""

    exc: AstExpr | None = None
    cause: AstExpr | None = None
