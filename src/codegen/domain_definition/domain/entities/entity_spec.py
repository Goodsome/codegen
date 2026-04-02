from codegen.domain_definition.domain.core.domain_concept import DomainConcept

from codegen.shared.domain.core import Entity


class EntitySpec(Entity, DomainConcept):
    """Specification of an entity."""

    __concept_name__ = "entity"
    __pkg_name__ = "entities"
