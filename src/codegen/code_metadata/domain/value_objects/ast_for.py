from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstFor(AstStmt):
    """Represents an ast.For node."""

    target: AstExpr
    iter: AstExpr
    body: list[AstStmt] = field(default_factory=list)
    orelse: list[AstStmt] = field(default_factory=list)
