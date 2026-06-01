from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_arguments import AstArguments
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
    from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt


class AstFunctionDef(ValueObject):
    kind: Literal[AstStmtKind.FUNCTION_DEF] = AstStmtKind.FUNCTION_DEF
    name: str
    args: AstArguments
    body: list[AstStmt] = Field(default_factory=list)
    decorator_list: list[AstExpr] = Field(default_factory=list)
    returns: AstExpr | None = None
    type_comment: str | None = None
