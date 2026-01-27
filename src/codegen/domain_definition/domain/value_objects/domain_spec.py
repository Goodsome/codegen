from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.domain_definition.domain.value_objects.value_object_spec import (
    ValueObjectSpec,
)
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.enum_spec import EnumSpec
from pydantic import Field
from codegen.shared.models import ValueObject


class DomainSpec(ValueObject):
    """Specification of a domain to be generated."""

    aggregates: list[AggregateSpec] = Field(default_factory=list)
    enums: list[EnumSpec] = Field(default_factory=list)
    value_objects: list[ValueObjectSpec] = Field(default_factory=list)
    entities: list[EntitySpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)

    def add_aggregate(self, aggregate: AggregateSpec) -> "DomainSpec":
        if any(a.name == aggregate.name for a in self.aggregates):
            raise ValueError(f"Aggregate '{aggregate.name}' already exists.")
        return self.model_copy(update={"aggregates": self.aggregates + [aggregate]})

    def update_aggregate(self, aggregate: AggregateSpec) -> "DomainSpec":
        if not any(a.name == aggregate.name for a in self.aggregates):
            raise ValueError(f"Aggregate '{aggregate.name}' not found.")
        new_list = [
            aggregate if x.name == aggregate.name else x for x in self.aggregates
        ]
        return self.model_copy(update={"aggregates": new_list})

    def delete_aggregate(self, name: str) -> "DomainSpec":
        new_list = [x for x in self.aggregates if str(x.name) != name]
        if len(new_list) == len(self.aggregates):
            raise ValueError(f"Aggregate '{name}' not found.")
        return self.model_copy(update={"aggregates": new_list})

    def add_value_object(self, value_object: ValueObjectSpec) -> "DomainSpec":
        if any(x.name == value_object.name for x in self.value_objects):
            raise ValueError(f"Value Object '{value_object.name}' already exists.")
        return self.model_copy(
            update={"value_objects": self.value_objects + [value_object]}
        )

    def update_value_object(self, value_object: ValueObjectSpec) -> "DomainSpec":
        if not any(x.name == value_object.name for x in self.value_objects):
            raise ValueError(f"Value Object '{value_object.name}' not found.")
        new_list = [
            value_object if x.name == value_object.name else x
            for x in self.value_objects
        ]
        return self.model_copy(update={"value_objects": new_list})

    def delete_value_object(self, name: str) -> "DomainSpec":
        new_list = [x for x in self.value_objects if str(x.name) != name]
        if len(new_list) == len(self.value_objects):
            raise ValueError(f"Value Object '{name}' not found.")
        return self.model_copy(update={"value_objects": new_list})

    def add_enum(self, enum: EnumSpec) -> "DomainSpec":
        if any(x.name == enum.name for x in self.enums):
            raise ValueError(f"Enum '{enum.name}' already exists.")
        return self.model_copy(update={"enums": self.enums + [enum]})

    def update_enum(self, enum: EnumSpec) -> "DomainSpec":
        if not any(x.name == enum.name for x in self.enums):
            raise ValueError(f"Enum '{enum.name}' not found.")
        new_list = [enum if x.name == enum.name else x for x in self.enums]
        return self.model_copy(update={"enums": new_list})

    def delete_enum(self, name: str) -> "DomainSpec":
        new_list = [x for x in self.enums if str(x.name) != name]
        if len(new_list) == len(self.enums):
            raise ValueError(f"Enum '{name}' not found.")
        return self.model_copy(update={"enums": new_list})

    def add_entity(self, entity: EntitySpec) -> "DomainSpec":
        if any(x.name == entity.name for x in self.entities):
            raise ValueError(f"Entity '{entity.name}' already exists.")
        return self.model_copy(update={"entities": self.entities + [entity]})

    def update_entity(self, entity: EntitySpec) -> "DomainSpec":
        if not any(x.name == entity.name for x in self.entities):
            raise ValueError(f"Entity '{entity.name}' not found.")
        new_list = [entity if x.name == entity.name else x for x in self.entities]
        return self.model_copy(update={"entities": new_list})

    def delete_entity(self, name: str) -> "DomainSpec":
        new_list = [x for x in self.entities if str(x.name) != name]
        if len(new_list) == len(self.entities):
            raise ValueError(f"Entity '{name}' not found.")
        return self.model_copy(update={"entities": new_list})
        
    def add_service(self, service: ServiceSpec) -> "DomainSpec":
        if any(x.name == service.name for x in self.services):
            raise ValueError(f"Service '{service.name}' already exists.")
        return self.model_copy(update={"services": self.services + [service]})

    def update_service(self, service: ServiceSpec) -> "DomainSpec":
        if not any(x.name == service.name for x in self.services):
            raise ValueError(f"Service '{service.name}' not found.")
        new_list = [service if x.name == service.name else x for x in self.services]
        return self.model_copy(update={"services": new_list})

    def delete_service(self, name: str) -> "DomainSpec":
        new_list = [x for x in self.services if str(x.name) != name]
        if len(new_list) == len(self.services):
            raise ValueError(f"Service '{name}' not found.")
        return self.model_copy(update={"services": new_list})
        
    def add_port(self, port: PortSpec) -> "DomainSpec":
        if any(x.name == port.name for x in self.ports):
            raise ValueError(f"Port '{port.name}' already exists.")
        return self.model_copy(update={"ports": self.ports + [port]})

    def update_port(self, port: PortSpec) -> "DomainSpec":
        if not any(x.name == port.name for x in self.ports):
            raise ValueError(f"Port '{port.name}' not found.")
        new_list = [port if x.name == port.name else x for x in self.ports]
        return self.model_copy(update={"ports": new_list})

    def delete_port(self, name: str) -> "DomainSpec":
        new_list = [x for x in self.ports if str(x.name) != name]
        if len(new_list) == len(self.ports):
            raise ValueError(f"Port '{name}' not found.")
        return self.model_copy(update={"ports": new_list})
