from pydantic import BaseModel, Field, model_validator
from typing import Self

from codegen.shared.domain.enums import ContainerType, PrimitiveType, PythonBuiltinType


class ParsedType(BaseModel):
    origin: PrimitiveType | ContainerType | PythonBuiltinType | None
    args: tuple[Self, ...] = Field(default_factory=tuple)
    component_name: str | None = None
    
    @model_validator(mode="after")
    def validate_origin_or_component(self) -> Self:
            if self.origin is None and self.component_name is None:
                raise ValueError("`origin` 和 `component_name` 不能同时为 None")
            return self