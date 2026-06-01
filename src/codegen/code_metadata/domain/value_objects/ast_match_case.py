from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from codegen.code_metadata.domain.value_objects.match_pattern import MatchPattern
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
    from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt


class AstMatchCase(ValueObject):
    pattern: MatchPattern
    guard: Optional[AstExpr] = None
    body: list[AstStmt] = Field(default_factory=list)
