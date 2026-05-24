from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstAssign(AstStmt):
    """Represents an ast.Assign node."""

    targets: list[AstExpr] = field(default_factory=list)
    value: AstExpr | None = None
