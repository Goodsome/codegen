from codegen.python_gen.domain.enums import AssignmentFlavor
from pydantic import Field
from codegen.shared.models import ValueObject


class AssignmentSpec(ValueObject):
    """描述变量的赋值结构 (RHS)。 对应 AST 中的 value 节点。"""

    flavor: AssignmentFlavor
    content: str = Field(default_factory=str)
    is_factory: bool
