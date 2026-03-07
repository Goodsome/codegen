from codegen.shared.domain.enums import ContainerType
from pydantic import Field
from codegen.shared.models import ValueObject


class TypeDefinition(ValueObject):
    """类型定义的公共部分，被 AttributeSpec 和 MethodOutput 共同继承。"""

    type: str
    container: ContainerType = Field(default=ContainerType.NONE)
    optional: bool = Field(default_factory=bool)
    custom_type_string: str | None = Field(default=None)
