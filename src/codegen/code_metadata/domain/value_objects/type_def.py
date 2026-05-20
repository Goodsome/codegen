from typing import Self

from pydantic import Field

from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.core.value_object import ValueObject


class TypeDef(ValueObject):
    origin: ReferenceTarget
    args: tuple[Self, ...] = Field(default_factory=tuple)

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        if self.origin.component_id:
            result.add(self.origin.component_id)
        for arg in self.args:
            result.update(arg.get_component_ids())
        return result
