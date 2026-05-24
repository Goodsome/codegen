from dataclasses import dataclass, field
import ast

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstMatchCase:
    """Represents a match_case clause."""

    pattern: ast.pattern
    guard: AstExpr | None = None
    body: list[AstStmt] = field(default_factory=list)

