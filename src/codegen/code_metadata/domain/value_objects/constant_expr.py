from typing import Literal, Any
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core import ValueObject

class ConstantExpr(ValueObject):
    """描述字面量，例如: 42, "hello", True"""
    kind: Literal[ExprKind.CONSTANT] = ExprKind.CONSTANT
    value: Any

    def get_component_ids(self) -> set[ComponentId]:
        return set()
