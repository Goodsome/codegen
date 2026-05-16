from dataclasses import dataclass, field

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.policies.aggregate_policy import AggregatePolicy
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy
from codegen.code_metadata.domain.policies.entity_policy import EntityPolicy
from codegen.code_metadata.domain.policies.enum_policy import EnumPolicy
from codegen.code_metadata.domain.policies.value_object_policy import ValueObjectPolicy


@dataclass
class ComponentPolicyFactory:

    _registry: dict[ComponentType, ComponentPolicy] = field(init=False)

    def __post_init__(self):
        self._registry = {
            ComponentType.AGGREGATE: AggregatePolicy(),
            ComponentType.ENTITY: EntityPolicy(),
            ComponentType.VALUE_OBJECT: ValueObjectPolicy(),
            ComponentType.ENUM: EnumPolicy(),
        }

    def get_policy(self, component_type: ComponentType) -> ComponentPolicy:
        cp = self._registry.get(component_type)
        if cp is None:
            raise ValueError(f"Unknown component type: {component_type}")
        return cp