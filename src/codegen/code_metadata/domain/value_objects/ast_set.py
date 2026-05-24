from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstSet(AstExpr):
    """Represents an ast.Set node."""

    elts: list[AstExpr] = field(default_factory=list)
