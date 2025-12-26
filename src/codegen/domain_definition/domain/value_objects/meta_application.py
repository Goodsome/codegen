from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.domain_definition.domain.value_objects.meta_use_case import MetaUseCase


class MetaApplication(ValueObject):
    """Specification of an application to be generated."""

    use_cases: list[MetaUseCase] = Field(default_factory=list)
