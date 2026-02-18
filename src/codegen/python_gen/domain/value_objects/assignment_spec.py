from codegen.python_gen.domain.enums import AssignmentFlavor
from pydantic import Field
from codegen.shared.models import ValueObject
from typing import Any, Union
from codegen.python_gen.domain.value_objects.reference_spec import ReferenceSpec
from codegen.python_gen.domain.value_objects.call_spec import CallSpec
from codegen.python_gen.domain.value_objects.literal_spec import LiteralSpec


class AssignmentSpec(ValueObject):
    """描述变量的赋值结构 (RHS)。 对应 AST 中的 value 节点。"""

    flavor: AssignmentFlavor
    literal: LiteralSpec | None = Field(default=None)
    reference: ReferenceSpec | None = Field(default=None)
    call: CallSpec | None = Field(default=None)
    list_items: list["AssignmentSpec"] | None = Field(default=None)
    dict_items: dict[str, "AssignmentSpec"] | None = Field(default=None)
    code: str | None = Field(default=None)

    @classmethod
    def from_code(cls, code: str) -> "AssignmentSpec":
        return cls(flavor=AssignmentFlavor.CODE, code=code)

    @classmethod
    def from_literal(cls, value: Any) -> "AssignmentSpec":
        return cls(
            flavor=AssignmentFlavor.LITERAL,
            literal=LiteralSpec(value=value)
        )

    @classmethod
    def from_call(cls, func_name: str, args: list["AssignmentSpec"] | None = None, kwargs: dict[str, "AssignmentSpec"] | None = None) -> "AssignmentSpec":
        from codegen.python_gen.domain.value_objects.call_spec import CallSpec
        return cls(
            flavor=AssignmentFlavor.CALL,
            call=CallSpec(
                callee=func_name,
                args=args or [],
                kwargs=kwargs or {},
            )
        )

# Resolve forward references
from codegen.python_gen.domain.value_objects.call_spec import CallSpec
CallSpec.model_rebuild()
AssignmentSpec.model_rebuild()
