from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstAssign(ValueObject):
    kind: Literal[AstStmtKind.ASSIGN] = AstStmtKind.ASSIGN
    targets: list[AstExpr] = Field(default_factory=list)
    value: AstExpr | None = None

    @property
    def target(self):
        if len(self.targets) != 1:
            raise ValueError(f"targets must have exactly one element: {self=}")
        return self.targets[0]

    @property
    def annotation(self) -> None:
        return