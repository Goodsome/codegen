from dataclasses import dataclass, field
import ast

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstBoolOp(AstExpr):
    """Represents an ast.BoolOp node (boolean operation)."""

    op: ast.boolop
    values: list[AstExpr] = field(default_factory=list)
