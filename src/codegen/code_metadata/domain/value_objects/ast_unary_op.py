from typing import TYPE_CHECKING, Literal

from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.enums.unary_op import UnaryOp
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstUnaryOp(ValueObject):
    kind: Literal[AstExprKind.UNARY_OP] = AstExprKind.UNARY_OP
    op: UnaryOp
    operand: "AstExpr"
