from pathlib import Path

from pydantic import BaseModel, Field

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.value_objects.pascal_string import PascalString


class FileCollection(BaseModel):
    context: str
    type: ComponentType
    code: str
    name: PascalString
    path: Path
    import_components: set[ImportedComponent] = Field(default_factory=set)
    dependencies: dict[str, Component] = Field(default_factory=dict)
    id_dependencies: dict[ComponentId, Component] = Field(default_factory=dict)
    id_map: dict[str, ComponentId] = Field(default_factory=dict)

    def new_component(self) -> Component:
        return Component(
            id=ComponentId.create(),
            context=self.context,
            type=self.type,
            name=self.name,
            description="",
        )
