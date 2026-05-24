from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstList(AstExpr):
    """Represents an ast.List node."""

    elts: list[AstExpr] = field(default_factory=list)
