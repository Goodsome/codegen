import ast

from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.type_spec import TypeSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import ValueObject


class VariableSpec(ValueObject):
    """对应 Python 代码中的 name: type_spec = assignment_spec"""

    name: SnakeString
    type_spec: TypeSpec
    assignment: AssignmentSpec

    @classmethod
    def create(
        cls, name: str, type_spec: TypeSpec, assignment: AssignmentSpec,
    ) -> "VariableSpec":
        return cls(
            name=SnakeString(name),
            type_spec=type_spec,
            assignment=assignment,
        )

    @classmethod
    def from_ast(cls, node: ast.AnnAssign) -> "VariableSpec":
        ...
    
    def to_ast(self) -> ast.AnnAssign:
        ...