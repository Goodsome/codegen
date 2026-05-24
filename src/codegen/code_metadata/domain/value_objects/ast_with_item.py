from typing import TYPE_CHECKING, Optional

from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstWithItem(ValueObject):
    context_expr: "AstExpr"
    optional_vars: Optional["AstExpr"] = None
