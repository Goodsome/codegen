
from codegen.domain_definition.domain.core.domain_concept import DomainConcept

from codegen.shared.models import Entity


class EntitySpec(Entity, DomainConcept):
    """Specification of an entity."""

    __pkg_name__ = "entities"
