from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.shared.domain.core import Entity


class DtoSpec(Entity, DomainConcept):
    """Specification of a DTO to be generated."""

    __concept_name__ = "dto"
    __pkg_name__ = "dtos"
