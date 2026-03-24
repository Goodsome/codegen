from typing import Any

from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import ValueObject
from pydantic import Field


class ConfigFieldSpec(ValueObject):
    """Specification for a single configuration field."""

    name: SnakeString
    type: str
    default: Any | None = Field(default=None)
    description: str = Field(default="")
    env_var: str | None = Field(default=None)

    def to_variable_spec(self) -> VariableSpec:
        """将 ConfigFieldSpec 转换为 VariableSpec"""
        type_spec = TypeAnnotationSpec.from_raw(self.type)
        if self.default is not None:
            assignment = AssignmentSpec.from_literal(self.default)
        else:
            assignment = None
        return VariableSpec.create(
            name=str(self.name),
            type_spec=type_spec,
            assignment=assignment,
        )
