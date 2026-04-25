from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.shared.domain.core import Entity


class DomainExceptionSpec(Entity, DomainConcept):
    """Specification of a domain exception to be generated."""

    __concept_name__ = "domain_exception"
    __pkg_name__ = "exceptions"
