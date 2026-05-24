from typing import TYPE_CHECKING, Literal, Optional

from pydantic import Field

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstAssign(ValueObject):
    kind: Literal[AstStmtKind.ASSIGN] = AstStmtKind.ASSIGN
    targets: list["AstExpr"] = Field(default_factory=list)
    value: Optional["AstExpr"] = None
