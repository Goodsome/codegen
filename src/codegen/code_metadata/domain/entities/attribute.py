from typing import Self

from pydantic import Field

from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.entity import Entity


class Attribute(Entity):
    id: AttributeId
    name: str
    type: TypeDef

    description: str = Field(default="")

    @classmethod
    def create(cls, sync_data: AttributeSyncData) -> Self:
        return cls(
            id=AttributeId.create(),
            name=sync_data.name,
            type=sync_data.type,
        )

    def update(self, sync_data: AttributeSyncData) -> None:
        self.name = sync_data.name
        self.type = sync_data.type

    def get_component_ids(self) -> set[ComponentId]:
        return self.type.get_component_ids()