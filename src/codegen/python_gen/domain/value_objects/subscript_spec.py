from typing import TYPE_CHECKING
from codegen.shared.models import ValueObject

if TYPE_CHECKING:
    from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec

class SubscriptSpec(ValueObject):
    """下标访问语法 obj[key]，对应 AST Subscript 节点。"""

    value: "AssignmentSpec" 
    slice: "AssignmentSpec"

    def get_required_types(self) -> set[str]:
        """收集 subscript.value 和 subscript.slice 中的所有类型标记。"""
        types: set[str] = set()
        types.update(self.value.get_required_types())
        types.update(self.slice.get_required_types())
        return types
