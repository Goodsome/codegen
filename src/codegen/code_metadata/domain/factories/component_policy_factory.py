from dataclasses import dataclass, field

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies import (
    AggregatePolicy,
    CorePolicy,
    EntityPolicy,
    EnumPolicy,
    ExternalPolicy,
    IdentifierPolicy,
    ValueObjectPolicy,
)
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


@dataclass
class ComponentPolicyFactory:
    _policies: list[ComponentPolicy] = field(init=False)
    _registry: dict[ComponentType, ComponentPolicy] = field(init=False)

    def __post_init__(self):
        self._policies = [
            AggregatePolicy(),
            CorePolicy(),
            EntityPolicy(),
            EnumPolicy(),
            ExternalPolicy(),
            ValueObjectPolicy(),
            IdentifierPolicy(),
        ]
        self._registry = {p.component_type: p for p in self._policies}

    def get_policy(self, component_type: ComponentType) -> ComponentPolicy:
        cp = self._registry.get(component_type)
        if cp is None:
            raise ValueError(f"Unknown component type: {component_type}")
        return cp

    def get_policies(self) -> list[ComponentPolicy]:
        return self._policies

    def get_dir_to_type_registry(self) -> dict[ComponentDir, ComponentType]:
        return {
            p.dir_name: p.component_type
            for p in self._policies
            if p.component_type is not ComponentType.EXTERNAL
        }
        