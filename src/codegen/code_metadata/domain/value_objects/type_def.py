from typing import Self

from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.value_object import ValueObject
from codegen.shared.domain.enums import ContainerType, PrimitiveType


class TypeDef(ValueObject):
    
    origin: PrimitiveType | ComponentId | ContainerType
    args: tuple[Self]