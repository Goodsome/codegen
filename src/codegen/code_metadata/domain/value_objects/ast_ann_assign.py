from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstAnnAssign(ValueObject):
    kind: Literal[AstStmtKind.ANN_ASSIGN] = AstStmtKind.ANN_ASSIGN
    target: AstExpr
    annotation: AstExpr
    value: Optional[AstExpr] = None
    simple: int = 1
