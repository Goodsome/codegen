from dataclasses import dataclass, field

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy
from codegen.code_metadata.domain.policies import AggregatePolicy, CorePolicy, EntityPolicy, EnumPolicy, ValueObjectPolicy



@dataclass
class ComponentPolicyFactory:

    _registry: dict[ComponentType, ComponentPolicy] = field(init=False)

    def __post_init__(self):
        policis = [
            AggregatePolicy,
            CorePolicy,
            EntityPolicy,
            EnumPolicy,
            ValueObjectPolicy,
        ]
        self._registry = {}
        for p in policis:
            self._registry[p.component_type] = p()

    def get_policy(self, component_type: ComponentType) -> ComponentPolicy:
        cp = self._registry.get(component_type)
        if cp is None:
            raise ValueError(f"Unknown component type: {component_type}")
        return cp