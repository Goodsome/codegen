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

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        domain: MetaDomain | None = None,
        application: MetaApplication | None = None,
        infrastructure: MetaInfrastructure | None = None,
    ):
        if domain is None:
            domain = MetaDomain()
        if application is None:
            application = MetaApplication()
        if infrastructure is None:
            infrastructure = MetaInfrastructure()
        return cls(
            name=name,
            description=description,
            domain=domain,
            application=application,
            infrastructure=infrastructure,
        )
