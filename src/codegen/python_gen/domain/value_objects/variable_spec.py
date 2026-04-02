from pydantic import Field

from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.core import ValueObject


class VariableSpec(ValueObject):
    """对应 Python 代码中的 name: type_spec = assignment_spec"""

    name: SnakeString
    type_spec: TypeAnnotationSpec | None = Field(default=None)
    assignment: AssignmentSpec | None = Field(default=None)

    @classmethod
    def create(
        cls,
        name: str,
        type_spec: TypeAnnotationSpec | None,
        assignment: AssignmentSpec | None = None,
    ) -> "VariableSpec":
        return cls(
            name=SnakeString(name),
            type_spec=type_spec,
            assignment=assignment,
        )

    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        if self.type_spec:
            types.update(self.type_spec.get_all_referenced_names())
        if self.assignment:
            types.update(self.assignment.get_required_types())
        return types
