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
