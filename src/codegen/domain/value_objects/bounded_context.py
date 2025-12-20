"""
Kind: ValueObject
Name: BoundedContext
Description: A logical boundary within the system.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.domain.value_objects.meta_application import MetaApplication

from codegen.domain.value_objects.meta_domain import MetaDomain

from codegen.domain.value_objects.meta_domain_port import MetaDomainPort
from codegen.domain.value_objects.meta_infrastructure import MetaInfrastructure
from codegen.domain.value_objects.meta_infrastructure_adapter import (
    MetaInfrastructureAdapter,
)
from codegen.domain.value_objects.meta_service import MetaService
from codegen.domain.value_objects.meta_use_case import MetaUseCase
from codegen.domain.value_objects.meta_value_object import MetaValueObject


class BoundedContext(ValueObject):
    """A logical boundary within the system."""

    name: str
    description: str
    domain: MetaDomain
    application: MetaApplication
    infrastructure: MetaInfrastructure

    @property
    def aggregates(self) -> list[MetaAggregate]:
        return self.domain.aggregates

    @property
    def value_objects(self) -> list[MetaValueObject]:
        return self.domain.value_objects

    @property
    def services(self) -> list[MetaService]:
        return self.domain.services

    @property
    def ports(self) -> list[MetaDomainPort]:
        return self.domain.ports

    @property
    def use_cases(self) -> list[MetaUseCase]:
        return self.application.use_cases

    @property
    def adapters(self) -> list[MetaInfrastructureAdapter]:
        return self.infrastructure.adapters
