from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase


@dataclass
class AstMatch(AstStmt):
    """Represents an ast.Match node (Python 3.10+)."""

    subject: AstExpr
    cases: list[AstMatchCase] = field(default_factory=list)
