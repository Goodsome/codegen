from pydantic import Field

from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.aggregate_root import AggregateRoot
from codegen.shared.domain.value_objects.snake_string import SnakeString


class Component(AggregateRoot[ComponentId]):
    """component"""
    
    type: ComponentType
    name: str
    description: str
    context: str

    bases: list[TypeDef] = Field(default_factory=list)

    attributes: list[Attribute] = Field(default_factory=list)
    behaviors: list[Behavior] = Field(default_factory=list)

    @property
    def file_name(self) -> str:
        return SnakeString(self.name)