from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.value_objects.attribute_sync_data import AttributeSyncData
from codegen.code_metadata.domain.value_objects.behavior_sync_data import BehaviorSyncData
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.value_object import ValueObject


class ComponentSyncData(ValueObject):
    context: str
    name: str
    type: ComponentType
    description: str
    bases: list[TypeDef]
    attributes: list[AttributeSyncData]
    behaviors: list[BehaviorSyncData]
    