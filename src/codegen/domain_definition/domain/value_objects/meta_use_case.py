from codegen.domain_definition.domain.value_objects.meta_use_case_result import (
    UseCaseResultSpec,
)
from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.attribute import AttributeSpec
from codegen.domain_definition.domain.value_objects.meta_use_case_query import (
    UseCaseQuerySpec,
)
from codegen.domain_definition.domain.value_objects.meta_use_case_command import (
    UseCaseCommandSpec,
)


class UseCaseSpec(ValueObject):
    """Specification of a use case to be generated."""

    name: str
    kind: str
    attributes: list[AttributeSpec] = Field(default_factory=list)
    description: str = Field(default_factory=str)
    command: UseCaseCommandSpec = Field(default_factory=UseCaseCommandSpec)
    query: UseCaseQuerySpec = Field(default_factory=UseCaseQuerySpec)
    result: UseCaseResultSpec = Field(default_factory=UseCaseResultSpec)

    @classmethod
    def create(
        cls,
        name: str,
        kind: str,
        attributes: list[AttributeSpec] | None = None,
        description: str = "",
        command: UseCaseCommandSpec | None = None,
        query: UseCaseQuerySpec | None = None,
        result: UseCaseResultSpec | None = None,
    ):
        if attributes is None:
            attributes = []
        if command is None:
            command = UseCaseCommandSpec()
        if query is None:
            query = UseCaseQuerySpec()
        if result is None:
            result = UseCaseResultSpec()
        return cls(
            name=name,
            kind=kind,
            attributes=attributes,
            description=description,
            command=command,
            query=query,
            result=result,
        )
