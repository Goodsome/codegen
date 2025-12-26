from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.meta_application import (
    MetaApplication,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    MetaInfrastructure,
)
from codegen.domain_definition.domain.value_objects.meta_domain import MetaDomain
from pydantic import Field


class BoundedContext(ValueObject):
    """A logical boundary within the system."""

    name: str
    description: str = Field(default_factory=str)
    domain: MetaDomain = Field(default_factory=MetaDomain)
    application: MetaApplication = Field(default_factory=MetaApplication)
    infrastructure: MetaInfrastructure = Field(default_factory=MetaInfrastructure)
