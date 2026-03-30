from typing import Self

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
from codegen.shared.domain.value_objects.pascal_string import PascalString
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

    def upsert_aggregate(self, name: str, description: str) -> Self:
        """Upsert an AggregateSpec by name. Only updates scalar fields if exists."""
        for agg in self.aggregates:
            if agg.name == name:
                agg.update_metadata(description=description)
                return self
        new_aggregate = AggregateSpec(name=PascalString(name), description=description)
        self.aggregates.append(new_aggregate)
        return self

    def get_aggregate(self, name: str) -> AggregateSpec:
        """Get an AggregateSpec by name. Raises ValueError if not found."""
        for agg in self.aggregates:
            if agg.name == name:
                return agg
        raise ValueError(f"Aggregate '{name}' not found in domain")

    def remove_aggregate(self, name: str) -> Self:
        """Remove an AggregateSpec by name. Returns self for chaining."""
        self.aggregates = [agg for agg in self.aggregates if agg.name != name]
        return self

    def upsert_enum(self, name: str, description: str = "") -> Self:
        """Upsert an EnumSpec by name. Only updates scalar fields if exists."""
        for e in self.enums:
            if e.name == name:
                e.update_metadata(description=description)
                return self
        new_enum = EnumSpec(name=PascalString(name), description=description, members=[])
        self.enums.append(new_enum)
        return self

    def get_enum(self, name: str) -> EnumSpec:
        """Get an EnumSpec by name. Raises ValueError if not found."""
        for e in self.enums:
            if e.name == name:
                return e
        raise ValueError(f"Enum '{name}' not found in domain")

    def remove_enum(self, name: str) -> Self:
        """Remove an EnumSpec by name. Returns self for chaining."""
        self.enums = [e for e in self.enums if e.name != name]
        return self

    def upsert_value_object(self, name: str, description: str)-> Self:
        """Upsert a ValueObjectSpec by name. Only updates scalar fields if exists."""
        for vo in self.value_objects:
            if vo.name == name:
                vo.update_metadata(description=description)
                return self
        new_vo = ValueObjectSpec(name=PascalString(name), description=description)
        self.value_objects.append(new_vo)
        return self

    def get_value_object(self, name: str) -> ValueObjectSpec:
        """Get a ValueObjectSpec by name. Raises ValueError if not found."""
        for vo in self.value_objects:
            if vo.name == name:
                return vo
        raise ValueError(f"ValueObject '{name}' not found in domain")

    def remove_value_object(self, name: str) -> Self:
        """Remove a ValueObjectSpec by name. Returns self for chaining."""
        self.value_objects = [vo for vo in self.value_objects if vo.name != name]
        return self

    def upsert_entity(self, name: str, description: str = "") -> Self:
        """Upsert an EntitySpec by name. Only updates scalar fields if exists."""
        for entity in self.entities:
            if entity.name == name:
                entity.update_metadata(description=description)
                return self
        new_entity = EntitySpec(name=PascalString(name), description=description)
        self.entities.append(new_entity)
        return self

    def get_entity(self, name: str) -> EntitySpec:
        """Get an EntitySpec by name. Raises ValueError if not found."""
        for entity in self.entities:
            if entity.name == name:
                return entity
        raise ValueError(f"Entity '{name}' not found in domain")

    def remove_entity(self, name: str) -> Self:
        """Remove an EntitySpec by name. Returns self for chaining."""
        self.entities = [e for e in self.entities if e.name != name]
        return self

    def upsert_service(self, name: str, description: str = "") -> Self:
        """Upsert a ServiceSpec by name. Only updates scalar fields if exists."""
        for svc in self.services:
            if svc.name == name:
                svc.update_metadata(description=description)
                return self
        new_service = ServiceSpec(name=PascalString(name), description=description)
        self.services.append(new_service)
        return self

    def get_service(self, name: str) -> ServiceSpec:
        """Get a ServiceSpec by name. Raises ValueError if not found."""
        for svc in self.services:
            if svc.name == name:
                return svc
        raise ValueError(f"Service '{name}' not found in domain")

    def remove_service(self, name: str) -> Self:
        """Remove a ServiceSpec by name. Returns self for chaining."""
        self.services = [s for s in self.services if s.name != name]
        return self

    def upsert_port(self, name: str, kind: str, description: str, aggregate: str | None) -> Self:
        """Upsert a PortSpec by name. Only updates scalar fields if exists."""
        for port in self.ports:
            if port.name == name:
                port.update_metadata(
                    kind=kind,
                    description=description,
                    aggregate=aggregate
                )
                return self
        new_port = PortSpec.create(name=PascalString(name), kind=kind, description=description)
        self.ports.append(new_port)
        return self

    def get_port(self, name: str) -> PortSpec:
        """Get a PortSpec by name. Raises ValueError if not found."""
        for port in self.ports:
            if port.name == name:
                return port
        raise ValueError(f"Port '{name}' not found in domain")

    def remove_port(self, name: str) -> Self:
        """Remove a PortSpec by name. Returns self for chaining."""
        self.ports = [p for p in self.ports if p.name != name]
        return self

