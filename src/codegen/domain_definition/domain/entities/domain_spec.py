from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.entities.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.entities.core_spec import CoreSpec
from codegen.domain_definition.domain.entities.domain_event_spec import DomainEventSpec
from codegen.domain_definition.domain.entities.domain_exception_spec import DomainExceptionSpec
from codegen.domain_definition.domain.entities.entity_spec import EntitySpec
from codegen.domain_definition.domain.entities.enum_spec import EnumSpec
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.entities.value_object_spec import ValueObjectSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.core import Entity


class DomainSpec(Entity):
    """Specification of a domain to be generated."""

    core: list[CoreSpec] = Field(default_factory=list)
    aggregates: list[AggregateSpec] = Field(default_factory=list)
    enums: list[EnumSpec] = Field(default_factory=list)
    value_objects: list[ValueObjectSpec] = Field(default_factory=list)
    entities: list[EntitySpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
    domain_events: list[DomainEventSpec] = Field(default_factory=list)
    domain_exceptions: list[DomainExceptionSpec] = Field(default_factory=list)

    def to_package_spec(self: Self) -> PackageSpec:
        """将 DomainSpec 转换为 PackageSpec"""
        aggregate_pkg = AggregateSpec.to_package_spec(self.aggregates)
        entity_pkg = EntitySpec.to_package_spec(self.entities)
        value_objects_pkg = ValueObjectSpec.to_package_spec(self.value_objects)
        services_pkg = ServiceSpec.to_package_spec(self.services)
        ports_pkg = PortSpec.to_package_spec(self.ports)
        core_pkg = CoreSpec.to_package_spec(self.core)
        domain_events_pkg = DomainEventSpec.to_package_spec(self.domain_events)
        domain_exceptions_pkg = DomainExceptionSpec.to_package_spec(self.domain_exceptions)
        sub_packages = [
            aggregate_pkg,
            entity_pkg,
            value_objects_pkg,
            services_pkg,
            ports_pkg,
            core_pkg,
            domain_events_pkg,
            domain_exceptions_pkg,
        ]
        modules: list[ModuleSpec] = []
        if self.enums:
            modules.append(EnumSpec.to_module_spec(self.enums))
        return PackageSpec.create(
            name="domain", sub_packages=sub_packages, modules=modules
        )

    @classmethod
    def from_package_spec(cls: type[Self], package_spec: PackageSpec) -> Self:
        """将 PackageSpec 逆向解析为 DomainSpec"""
        aggregates = []
        entities = []
        value_objects = []
        services = []
        ports = []
        enums: list[EnumSpec] = []
        core = []
        domain_events = []
        domain_exceptions = []
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
            elif pkg.name == "core":
                core = CoreSpec.from_package_spec(pkg)
            elif pkg.name == "events":
                domain_events = DomainEventSpec.from_package_spec(pkg)
            elif pkg.name == "exceptions":
                domain_exceptions = DomainExceptionSpec.from_package_spec(pkg)

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
            core=core,
            domain_events=domain_events,
            domain_exceptions=domain_exceptions,
        )

    def add_aggregate(self: Self, aggregate: AggregateSpec) -> Self:
        """Add an AggregateSpec. Raises ValueError if aggregate with same name exists."""
        for agg in self.aggregates:
            if agg.name == aggregate.name:
                raise ValueError(
                    f"Aggregate '{aggregate.name}' already exists in domain"
                )
        self.aggregates.append(aggregate)
        return self

    def update_aggregate(self: Self, aggregate: AggregateSpec) -> Self:
        """Update an existing AggregateSpec by name. Raises ValueError if not found."""
        for i, agg in enumerate(self.aggregates):
            if agg.name == aggregate.name:
                self.aggregates[i] = aggregate
                return self
        raise ValueError(f"Aggregate '{aggregate.name}' not found in domain")

    def get_aggregate(self: Self, name: str) -> AggregateSpec:
        """Get an AggregateSpec by name. Raises ValueError if not found."""
        for agg in self.aggregates:
            if agg.name == name:
                return agg
        raise ValueError(f"Aggregate '{name}' not found in domain")

    def remove_aggregate(self: Self, name: str) -> Self:
        """Remove an AggregateSpec by name. Returns self for chaining."""
        self.aggregates = [agg for agg in self.aggregates if agg.name != name]
        return self

    def add_enum(self: Self, enum: EnumSpec) -> Self:
        """Add an EnumSpec. Raises ValueError if enum with same name exists."""
        for e in self.enums:
            if e.name == enum.name:
                raise ValueError(f"Enum '{enum.name}' already exists in domain")
        self.enums.append(enum)
        return self

    def update_enum(self: Self, enum: EnumSpec) -> Self:
        """Update an existing EnumSpec by name. Raises ValueError if not found."""
        for i, e in enumerate(self.enums):
            if e.name == enum.name:
                self.enums[i] = enum
                return self
        raise ValueError(f"Enum '{enum.name}' not found in domain")

    def get_enum(self: Self, name: str) -> EnumSpec:
        """Get an EnumSpec by name. Raises ValueError if not found."""
        for e in self.enums:
            if e.name == name:
                return e
        raise ValueError(f"Enum '{name}' not found in domain")

    def remove_enum(self: Self, name: str) -> Self:
        """Remove an EnumSpec by name. Returns self for chaining."""
        self.enums = [e for e in self.enums if e.name != name]
        return self

    def add_value_object(self: Self, value_object: ValueObjectSpec) -> Self:
        """Add a ValueObjectSpec. Raises ValueError if value object with same name exists."""
        for vo in self.value_objects:
            if vo.name == value_object.name:
                raise ValueError(
                    f"ValueObject '{value_object.name}' already exists in domain"
                )
        self.value_objects.append(value_object)
        return self

    def update_value_object(self: Self, value_object: ValueObjectSpec) -> Self:
        """Update an existing ValueObjectSpec by name. Raises ValueError if not found."""
        for i, vo in enumerate(self.value_objects):
            if vo.name == value_object.name:
                self.value_objects[i] = value_object
                return self
        raise ValueError(f"ValueObject '{value_object.name}' not found in domain")

    def get_value_object(self: Self, name: str) -> ValueObjectSpec:
        """Get a ValueObjectSpec by name. Raises ValueError if not found."""
        for vo in self.value_objects:
            if vo.name == name:
                return vo
        raise ValueError(f"ValueObject '{name}' not found in domain")

    def remove_value_object(self: Self, name: str) -> Self:
        """Remove a ValueObjectSpec by name. Returns self for chaining."""
        self.value_objects = [vo for vo in self.value_objects if vo.name != name]
        return self

    def add_domain_event(self: Self, domain_event: DomainEventSpec) -> Self:
        """Add a DomainEventSpec. Raises ValueError if domain event with same name exists."""
        for de in self.domain_events:
            if de.name == domain_event.name:
                raise ValueError(
                    f"DomainEvent '{domain_event.name}' already exists in domain"
                )
        self.domain_events.append(domain_event)
        return self

    def update_domain_event(self: Self, domain_event: DomainEventSpec) -> Self:
        """Update an existing DomainEventSpec by name. Raises ValueError if not found."""
        for i, de in enumerate(self.domain_events):
            if de.name == domain_event.name:
                self.domain_events[i] = domain_event
                return self
        raise ValueError(f"DomainEvent '{domain_event.name}' not found in domain")

    def get_domain_event(self: Self, name: str) -> DomainEventSpec:
        """Get a DomainEventSpec by name. Raises ValueError if not found."""
        for de in self.domain_events:
            if de.name == name:
                return de
        raise ValueError(f"DomainEvent '{name}' not found in domain")

    def remove_domain_event(self: Self, name: str) -> Self:
        """Remove a DomainEventSpec by name. Returns self for chaining."""
        self.domain_events = [de for de in self.domain_events if de.name != name]
        return self

    def add_domain_exception(self: Self, domain_exception: DomainExceptionSpec) -> Self:
        """Add a DomainExceptionSpec. Raises ValueError if domain exception with same name exists."""
        for de in self.domain_exceptions:
            if de.name == domain_exception.name:
                raise ValueError(
                    f"DomainException '{domain_exception.name}' already exists in domain"
                )
        self.domain_exceptions.append(domain_exception)
        return self

    def update_domain_exception(self: Self, domain_exception: DomainExceptionSpec) -> Self:
        """Update an existing DomainExceptionSpec by name. Raises ValueError if not found."""
        for i, de in enumerate(self.domain_exceptions):
            if de.name == domain_exception.name:
                self.domain_exceptions[i] = domain_exception
                return self
        raise ValueError(f"DomainException '{domain_exception.name}' not found in domain")

    def get_domain_exception(self: Self, name: str) -> DomainExceptionSpec:
        """Get a DomainExceptionSpec by name. Raises ValueError if not found."""
        for de in self.domain_exceptions:
            if de.name == name:
                return de
        raise ValueError(f"DomainException '{name}' not found in domain")

    def remove_domain_exception(self: Self, name: str) -> Self:
        """Remove a DomainExceptionSpec by name. Returns self for chaining."""
        self.domain_exceptions = [de for de in self.domain_exceptions if de.name != name]
        return self

    def add_entity(self: Self, entity: EntitySpec) -> Self:
        """Add an EntitySpec. Raises ValueError if entity with same name exists."""
        for e in self.entities:
            if e.name == entity.name:
                raise ValueError(f"Entity '{entity.name}' already exists in domain")
        self.entities.append(entity)
        return self

    def update_entity(self: Self, entity: EntitySpec) -> Self:
        """Update an existing EntitySpec by name. Raises ValueError if not found."""
        for i, e in enumerate(self.entities):
            if e.name == entity.name:
                self.entities[i] = entity
                return self
        raise ValueError(f"Entity '{entity.name}' not found in domain")

    def get_entity(self: Self, name: str) -> EntitySpec:
        """Get an EntitySpec by name. Raises ValueError if not found."""
        for entity in self.entities:
            if entity.name == name:
                return entity
        raise ValueError(f"Entity '{name}' not found in domain")

    def remove_entity(self: Self, name: str) -> Self:
        """Remove an EntitySpec by name. Returns self for chaining."""
        self.entities = [e for e in self.entities if e.name != name]
        return self

    def add_service(self: Self, service: ServiceSpec) -> Self:
        """Add a ServiceSpec. Raises ValueError if service with same name exists."""
        for s in self.services:
            if s.name == service.name:
                raise ValueError(f"Service '{service.name}' already exists in domain")
        self.services.append(service)
        return self

    def update_service(self: Self, service: ServiceSpec) -> Self:
        """Update an existing ServiceSpec by name. Raises ValueError if not found."""
        for i, s in enumerate(self.services):
            if s.name == service.name:
                self.services[i] = service
                return self
        raise ValueError(f"Service '{service.name}' not found in domain")

    def get_service(self: Self, name: str) -> ServiceSpec:
        """Get a ServiceSpec by name. Raises ValueError if not found."""
        for svc in self.services:
            if svc.name == name:
                return svc
        raise ValueError(f"Service '{name}' not found in domain")

    def remove_service(self: Self, name: str) -> Self:
        """Remove a ServiceSpec by name. Returns self for chaining."""
        self.services = [s for s in self.services if s.name != name]
        return self

    def add_port(self: Self, port: PortSpec) -> Self:
        """Add a PortSpec. Raises ValueError if port with same name exists."""
        for p in self.ports:
            if p.name == port.name:
                raise ValueError(f"Port '{port.name}' already exists in domain")
        self.ports.append(port)
        return self

    def update_port(self: Self, port: PortSpec) -> Self:
        """Update an existing PortSpec by name. Raises ValueError if not found."""
        for i, p in enumerate(self.ports):
            if p.name == port.name:
                self.ports[i] = port
                return self
        raise ValueError(f"Port '{port.name}' not found in domain")

    def get_port(self: Self, name: str) -> PortSpec:
        """Get a PortSpec by name. Raises ValueError if not found."""
        for port in self.ports:
            if port.name == name:
                return port
        raise ValueError(f"Port '{name}' not found in domain")

    def remove_port(self: Self, name: str) -> Self:
        """Remove a PortSpec by name. Returns self for chaining."""
        self.ports = [p for p in self.ports if p.name != name]
        return self

    def get_core(self: Self, name: str) -> CoreSpec:
        """Get a CoreSpec by name. Raises ValueError if not found."""
        for core in self.core:
            if core.name == name:
                return core
        raise ValueError(f"Core '{name}' not found in domain")

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create test package for domain with aggregates that have rules."""
        sp: list[PackageSpec] = []
        sp += [agg.to_test_package_spec() for agg in self.aggregates]
        sp += [entity.to_test_package_spec() for entity in self.entities]
        sp += [
            value_object.to_test_package_spec() for value_object in self.value_objects
        ]
        sp += [
            domain_event.to_test_package_spec() for domain_event in self.domain_events
        ]
        sp += [
            domain_exception.to_test_package_spec() for domain_exception in self.domain_exceptions
        ]
        sp += [service.to_test_package_spec() for service in self.services]
        sp += [core.to_test_package_spec() for core in self.core]
        return PackageSpec.create(name="domain", sub_packages=sp)

    def load_test_package(self: Self, test_pkg: PackageSpec) -> Self:
        """Load test package into the domain spec. Returns self for chaining."""
        for pkg in test_pkg.sub_packages:
            # Load aggregate tests
            if pkg.name == "aggregates":
                for agg_pkg in pkg.sub_packages:
                    agg = self.get_aggregate(agg_pkg.name)
                    agg.load_test_package(agg_pkg)
            # Load entity tests
            elif pkg.name == "entities":
                for entity_pkg in pkg.sub_packages:
                    entity = self.get_entity(entity_pkg.name)
                    entity.load_test_package(entity_pkg)
            # Load value object tests
            elif pkg.name == "value_objects":
                for vo_pkg in pkg.sub_packages:
                    vo = self.get_value_object(vo_pkg.name)
                    vo.load_test_package(vo_pkg)
            # Load domain event tests
            elif pkg.name == "domain_events":
                for de_pkg in pkg.sub_packages:
                    de = self.get_domain_event(de_pkg.name)
                    de.load_test_package(de_pkg)
            # Load domain exception tests
            elif pkg.name == "domain_exceptions":
                for de_pkg in pkg.sub_packages:
                    de = self.get_domain_exception(de_pkg.name)
                    de.load_test_package(de_pkg)
            # Load service tests
            elif pkg.name == "services":
                for svc_pkg in pkg.sub_packages:
                    svc = self.get_service(svc_pkg.name)
                    svc.load_test_package(svc_pkg)
            # Load core tests
            elif pkg.name == "core":
                for core_pkg in pkg.sub_packages:
                    core = self.get_core(core_pkg.name)
                    core.load_test_package(core_pkg)
        return self
