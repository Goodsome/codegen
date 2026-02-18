from codegen.shared.models import ValueObject


class ReferenceSpec(ValueObject):
    """引用一个已存在的变量或符号 (对应 AST Name节点)。"""

    name: str
