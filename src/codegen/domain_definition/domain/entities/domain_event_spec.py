from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.shared.domain.core import Entity


class DomainEventSpec(Entity, DomainConcept):
    """Specification of a domain event to be generated."""

    __concept_name__ = "domain_event"
    __pkg_name__ = "events"
