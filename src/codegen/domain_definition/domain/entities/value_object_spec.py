from codegen.domain_definition.domain.core.domain_concept import DomainConcept

from codegen.shared.domain.core import Entity


class ValueObjectSpec(Entity, DomainConcept):
    """Specification of a value object to be generated."""

    __concept_name__ = "value_object"
    __pkg_name__ = "value_objects"
