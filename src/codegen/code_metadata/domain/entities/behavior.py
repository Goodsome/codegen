from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.identifiers.behavior_id import BehaviorId
from codegen.code_metadata.domain.value_objects.attribute_sync_data import AttributeSyncData
from codegen.code_metadata.domain.value_objects.behavior_sync_data import BehaviorSyncData
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

    @classmethod
    def create(cls, data: BehaviorSyncData):
        return cls(
            id=BehaviorId.create(),
            name=data.name,
            description=data.description,
            inputs=[Attribute.create(a) for a in data.inputs],
            output=data.output,
            scenarios=[]
        )

    def update(self, data: BehaviorSyncData):
        self.name = data.name
        self.description = data.description
        self.output = data.output
        
        self.sync_inputs(data.inputs)
        
    def sync_inputs(self, attributes: list[AttributeSyncData]) -> None:
        existing_attributes = {attr.name: attr for attr in self.inputs}
        synced_attrs: list[Attribute] = []
        for attr_sync_data in attributes:
            if attr_sync_data.name in existing_attributes:
                attr = existing_attributes[attr_sync_data.name]
                attr.update(attr_sync_data)
            else:
                attr = Attribute.create(attr_sync_data)

            synced_attrs.append(attr)
        self.inputs = synced_attrs
        