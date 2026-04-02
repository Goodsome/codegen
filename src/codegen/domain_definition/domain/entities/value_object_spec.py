
from codegen.domain_definition.domain.core.domain_concept import DomainConcept

from codegen.shared.models import Entity


class ValueObjectSpec(Entity, DomainConcept):
    """Specification of a value object to be generated."""

    __pkg_name__ = "value_objects"
