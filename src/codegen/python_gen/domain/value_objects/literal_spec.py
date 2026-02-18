from codegen.shared.models import ValueObject
from typing import Any


class LiteralSpec(ValueObject):
    """基础类型的字面量值 (对应 AST Constant节点)。"""

    value: Any
