from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.identifiers.behavior_id import BehaviorId
from codegen.code_metadata.domain.value_objects.scenario import Scenario
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.entity import Entity


class Behavior(Entity):

    id: BehaviorId
    name: str
    description: str
    scenarios: list[Scenario]
    inputs: list[Attribute]
    output: TypeDef