from codegen.python_gen.domain.enums import AssignmentFlavor
from pydantic import Field
from codegen.shared.models import ValueObject
from typing import Any
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
    def from_symbol(cls, symbol: str) -> "AssignmentSpec":
        return cls(
            flavor=AssignmentFlavor.SYMBOL,
            reference=ReferenceSpec(name=symbol)
        )

    @classmethod
    def from_call(cls, func_name: str, args: list["AssignmentSpec"] | None = None, kwargs: dict[str, "AssignmentSpec"] | None = None) -> "AssignmentSpec":
        return cls(
            flavor=AssignmentFlavor.CALL,
            call=CallSpec(
                callee=func_name,
                args=args or [],
                kwargs=kwargs or {},
            )
        )

    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        if self.flavor == AssignmentFlavor.CALL and self.call:
            types.add(self.call.callee)
            for arg in self.call.args:
                types.update(arg.get_required_types())
            for kwarg in self.call.kwargs.values():
                types.update(kwarg.get_required_types())
        elif self.flavor == AssignmentFlavor.SYMBOL and self.reference:
            types.add(self.reference.name)
        elif self.list_items:
            for item in self.list_items:
                types.update(item.get_required_types())
        elif self.dict_items:
            for item in self.dict_items.values():
                types.update(item.get_required_types())
        return types
