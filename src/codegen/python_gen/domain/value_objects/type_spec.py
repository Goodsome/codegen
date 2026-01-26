from codegen.shared.models import ValueObject
from codegen.shared.domain.enums import ContainerType


class TypeSpec(ValueObject):
    """描述变量的类型注解结构 (LHS)。 对应 AST 中的 annotation 节点。"""

    core_type: str
    container: ContainerType
    nullable: bool
