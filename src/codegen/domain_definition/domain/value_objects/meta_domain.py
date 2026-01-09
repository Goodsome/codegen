from codegen.domain_definition.domain.value_objects.meta_value_object import (
    ValueObjectSpec,
)
from codegen.domain_definition.domain.value_objects.meta_port import PortSpec
from codegen.domain_definition.domain.value_objects.meta_service import ServiceSpec
from codegen.domain_definition.domain.value_objects.meta_aggregate import AggregateSpec
from codegen.domain_definition.domain.value_objects.meta_enum import EnumSpec
from pydantic import Field
from codegen.shared.models import ValueObject


class DomainSpec(ValueObject):
    """Specification of a domain to be generated."""

    aggregates: list[AggregateSpec] = Field(default_factory=list)
    enums: list[EnumSpec] = Field(default_factory=list)
    value_objects: list[ValueObjectSpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
