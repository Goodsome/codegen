"""
Kind: ValueObject
Name: BoundedContext
Description: A logical boundary within the system.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.meta_application import MetaApplication

from codegen.domain.value_objects.meta_domain import MetaDomain

from codegen.domain.value_objects.meta_infrastructure import MetaInfrastructure


class BoundedContext(ValueObject):
    """A logical boundary within the system."""

    name: str

    description: str

    domain: MetaDomain

    application: MetaApplication

    infrastructure: MetaInfrastructure
