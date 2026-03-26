from typing import Any

from pydantic import Field

from codegen.domain_definition.domain.value_objects.type_definition import TypeDefinition
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString


class ConfigFieldSpec(TypeDefinition):
    """Specification for a single configuration field."""

    name: SnakeString
    type: str
    default: Any | None = Field(default=None)
    description: str = Field(default="")
    env_var: str | None = Field(default=None)

    def to_variable_spec(self) -> VariableSpec:
        """将 ConfigFieldSpec 转换为 VariableSpec"""
        annotation = self.to_python_annotation()
        if self.default is not None:
            assignment = AssignmentSpec.from_literal(self.default)
        else:
            assignment = None
        return VariableSpec.create(
            name=str(self.name),
            type_spec=annotation,
            assignment=assignment,
        )
