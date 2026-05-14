from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class Component(AggregateRoot):

    id: ComponentId
    type: ComponentType
    name: str
    description: str
    context: str
    
    attributes: list[Attribute]
    behaviors: list[Behavior]
    