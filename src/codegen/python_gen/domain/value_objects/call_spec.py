from codegen.shared.models import ValueObject
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec


class CallSpec(ValueObject):
    """函数调用或类实例化 (对应 AST Call节点)。"""

    callee: str
    args: list["AssignmentSpec"]
    kwargs: dict[str, "AssignmentSpec"]
