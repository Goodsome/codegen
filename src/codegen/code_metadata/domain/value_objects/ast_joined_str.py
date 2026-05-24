from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr

@dataclass
class AstJoinedStr(AstExpr):
    """Represents an ast.JoinedStr node (f-string)."""

    values: list[AstExpr] = field(default_factory=list)
