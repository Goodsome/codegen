from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstIf(AstStmt):
    """Represents an ast.If node."""

    test: AstExpr
    body: list[AstStmt] = field(default_factory=list)
    orelse: list[AstStmt] = field(default_factory=list)
