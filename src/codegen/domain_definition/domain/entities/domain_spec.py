from codegen.domain_definition.domain.entities.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.entities.entity_spec import EntitySpec
from codegen.domain_definition.domain.entities.enum_spec import EnumSpec
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.entities.value_object_spec import (
    ValueObjectSpec,
)
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.models import Entity
from pydantic import Field


class DomainSpec(Entity):
    """Specification of a domain to be generated."""

    aggregates: list[AggregateSpec] = Field(default_factory=list)
    enums: list[EnumSpec] = Field(default_factory=list)
    value_objects: list[ValueObjectSpec] = Field(default_factory=list)
    entities: list[EntitySpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)

    def to_package_spec(self) -> PackageSpec:
        """将 DomainSpec 转换为 PackageSpec"""
        aggregate_pkg = AggregateSpec.to_package_spec(self.aggregates)
        entity_pkg = EntitySpec.to_package_spec(self.entities)
        value_objects_pkg = ValueObjectSpec.to_package_spec(self.value_objects)
        services_pkg = ServiceSpec.to_package_spec(self.services)
        ports_pkg = PortSpec.to_package_spec(self.ports)
        sub_packages = [
            aggregate_pkg,
            entity_pkg,
            value_objects_pkg,
            services_pkg,
            ports_pkg,
        ]
        modules: list[ModuleSpec] = []
        if self.enums:
            modules.append(EnumSpec.to_module_spec(self.enums))
        return PackageSpec.create(
            name="domain",
            sub_packages=sub_packages,
            modules=modules,
        )

    @classmethod
    def from_package_spec(cls, package_spec: PackageSpec) -> "DomainSpec":
        """将 PackageSpec 逆向解析为 DomainSpec"""
        aggregates = []
        entities = []
        value_objects = []
        services = []
        ports = []
        enums: list[EnumSpec] = []

        for pkg in package_spec.sub_packages:
            if pkg.name == "aggregates":
                aggregates = AggregateSpec.from_package_spec(pkg)
            elif pkg.name == "entities":
                entities = EntitySpec.from_package_spec(pkg)
            elif pkg.name == "value_objects":
                value_objects = ValueObjectSpec.from_package_spec(pkg)
            elif pkg.name == "services":
                services = ServiceSpec.from_package_spec(pkg)
            elif pkg.name == "ports":
                ports = PortSpec.from_package_spec(pkg)
        for module in package_spec.modules:
            if module.name == "enums":
                enums = EnumSpec.from_module_spec(module)

        return cls(
            aggregates=aggregates,
            entities=entities,
            value_objects=value_objects,
            services=services,
            ports=ports,
            enums=enums,
        )

