from dataclasses import dataclass
import ast

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstUnaryOp(AstExpr):
    """Represents an ast.UnaryOp node (unary operation)."""

    op: ast.unaryop
    operand: AstExpr
