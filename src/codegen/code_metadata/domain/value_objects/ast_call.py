from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstCall(AstExpr):
    """Represents an ast.Call node."""

    func: AstExpr
    args: list[AstExpr] = field(default_factory=list)
    kwargs: dict[str, AstExpr] = field(default_factory=dict)
