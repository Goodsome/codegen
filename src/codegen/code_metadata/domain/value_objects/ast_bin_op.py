from dataclasses import dataclass
import ast

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstBinOp(AstExpr):
    """Represents an ast.BinOp node (binary operation)."""

    left: AstExpr
    op: ast.operator
    right: AstExpr
