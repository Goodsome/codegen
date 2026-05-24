from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstSlice(AstExpr):
    """Represents an ast.Slice node."""

    lower: AstExpr | None = None
    upper: AstExpr | None = None
    step: AstExpr | None = None
