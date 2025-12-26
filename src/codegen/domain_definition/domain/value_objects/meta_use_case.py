from codegen.domain_definition.domain.value_objects.meta_use_case_command import (
    MetaUseCaseCommand,
)
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.meta_use_case_result import (
    MetaUseCaseResult,
)
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import Attribute


class MetaUseCase(ValueObject):
    """Specification of a use case to be generated."""

    name: str
    attributes: list[Attribute] = Field(default_factory=list)
    kind: str
    description: str = Field(default_factory=str)
    command: MetaUseCaseCommand
    result: MetaUseCaseResult
