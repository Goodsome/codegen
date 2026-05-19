from typing import TYPE_CHECKING
from pydantic import Field
from typing_extensions import Literal
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
    

class SequenceExprDto(ValueObject):
    """描述容器字面量，例如: [1, 2, 3] 或 {"a": 1} (对应 ast.List, ast.Dict 等)"""
    kind: Literal[ExprKind.SEQUENCE] = ExprKind.SEQUENCE
    container_type: Literal["list", "tuple", "set"]
    elements: list["ParsedExpr"] = Field(default_factory=list)
