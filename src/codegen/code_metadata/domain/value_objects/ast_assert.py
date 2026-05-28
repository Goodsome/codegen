from typing import TYPE_CHECKING, Literal, Optional

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstAssert(ValueObject):
    kind: Literal[AstStmtKind.ASSERT] = AstStmtKind.ASSERT
    test: "AstExpr"
    msg: Optional["AstExpr"] = None
