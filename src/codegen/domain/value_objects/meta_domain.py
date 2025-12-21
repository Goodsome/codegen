"""
Kind: ValueObject
Name: MetaDomain
Description: Specification of a domain to be generated.
"""

from pydantic import Field

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.meta_aggregate import MetaAggregate

from codegen.domain.value_objects.meta_domain_port import MetaDomainPort

from codegen.domain.value_objects.meta_service import MetaService

from codegen.domain.value_objects.meta_value_object import MetaValueObject


class MetaDomain(ValueObject):
    """Specification of a domain to be generated."""

    aggregates: list[MetaAggregate] = Field(default_factory=list)
    value_objects: list[MetaValueObject] = Field(default_factory=list)
    services: list[MetaService] = Field(default_factory=list)
    ports: list[MetaDomainPort] = Field(default_factory=list)
