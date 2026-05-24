from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstTuple(AstExpr):
    """Represents an ast.Tuple node."""

    elts: list[AstExpr] = field(default_factory=list)
