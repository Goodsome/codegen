from typing import TYPE_CHECKING, Literal, Optional

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstReturn(ValueObject):
    kind: Literal[AstStmtKind.RETURN] = AstStmtKind.RETURN
    value: Optional["AstExpr"] = None
