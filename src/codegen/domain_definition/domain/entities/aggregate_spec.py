from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.shared.models import Entity


class AggregateSpec(Entity, DomainConcept):
    """Specification of a domain aggregate to be generated."""

    __concept_name__ = "aggregate_root"
    __pkg_name__ = "aggregates"
