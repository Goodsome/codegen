from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.shared.models import Entity

class CoreSpec(Entity, DomainConcept):
    """Specification of a core entity to be generated."""

    __pkg_name__ = "core"
