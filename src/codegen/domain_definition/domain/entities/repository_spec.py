from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.shared.domain.core import Entity


class RepositorySpec(Entity, DomainConcept):
    """Specification of a domain repository to be generated."""

    __concept_name__ = "repository"
    __pkg_name__ = "repositories"
