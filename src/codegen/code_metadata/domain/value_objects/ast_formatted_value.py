from typing import TYPE_CHECKING, Literal, Optional

from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstFormattedValue(ValueObject):
    kind: Literal[AstExprKind.FORMATTED_VALUE] = AstExprKind.FORMATTED_VALUE
    value: "AstExpr"
    conversion: int
    format_spec: Optional["AstExpr"] = None
