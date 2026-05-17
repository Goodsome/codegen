from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.shared.domain.core.entity import Entity


class InfraMapperSpec(Entity, DomainConcept):
    """Specification of a infrastructure mapper to be generated."""

    __concept_name__ = "mapper"
    __pkg_name__ = "mappers"
