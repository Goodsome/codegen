from dataclasses import dataclass, field

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies import (
    AggregatePolicy,
    ContextPolicy,
    CorePolicy,
    EntityPolicy,
    EnumPolicy,
    EventPolicy,
    ExceptionPolicy,
    ExternalPolicy,
    FactoryPolicy,
    IdentifierPolicy,
    MapperPolicy,
    RegistryPolicy,
    RepositoryPolicy,
    PolicyPolicy,
    OrmModelPolicy,
    GatewayPolicy,
    ServicePolicy,
    ValueObjectPolicy,
)
from codegen.code_metadata.domain.policies.adapter_policy import AdapterPolicy
from codegen.code_metadata.domain.policies.cli_policy import CliPolicy
from codegen.code_metadata.domain.policies.command_policy import CommandPolicy
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy
from codegen.code_metadata.domain.policies.database_policy import DatabasePolicy
from codegen.code_metadata.domain.policies.dto_policy import DtoPolicy
from codegen.code_metadata.domain.policies.port_policy import PortPolicy
from codegen.code_metadata.domain.policies.query_policy import QueryPolicy


@dataclass
class ComponentPolicyFactory:
    _policies: list[ComponentPolicy] = field(init=False)
    _registry: dict[ComponentType, ComponentPolicy] = field(init=False)

    def __post_init__(self):
        self._policies = [
            AggregatePolicy(),
            CorePolicy(),
            DtoPolicy(),
            EntityPolicy(),
            EnumPolicy(),
            ExternalPolicy(),
            ValueObjectPolicy(),
            IdentifierPolicy(),
            QueryPolicy(),
            CommandPolicy(),
            PortPolicy(),
            ServicePolicy(),
            MapperPolicy(),
            FactoryPolicy(),
            EventPolicy(),
            ExceptionPolicy(),
            RepositoryPolicy(),
            PolicyPolicy(),
            OrmModelPolicy(),
            GatewayPolicy(),
            ContextPolicy(),
            RegistryPolicy(),
            AdapterPolicy(),
            DatabasePolicy(),
            CliPolicy(),
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
        