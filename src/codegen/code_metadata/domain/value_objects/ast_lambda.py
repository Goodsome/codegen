from typing import TYPE_CHECKING, Literal

from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.lambda_args import LambdaArgs
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstLambda(ValueObject):
    kind: Literal[AstExprKind.LAMBDA] = AstExprKind.LAMBDA
    args: LambdaArgs
    body: "AstExpr"
