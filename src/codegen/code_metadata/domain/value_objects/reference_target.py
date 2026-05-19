from pydantic import model_validator, Field
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core import ValueObject
from codegen.shared.domain.enums import PythonBuiltinType


class ReferenceTarget(ValueObject):
    component_id: ComponentId | None = Field(default=None)
    attribute_id: AttributeId | None = Field(default=None)
    builtin_type: PythonBuiltinType | None = Field(default=None)
    
    @model_validator(mode="after")
    def validate_target(self) -> "ReferenceTarget":
        if self.component_id is not None:
            return self
        if self.attribute_id is not None:
            return self
        if self.builtin_type is not None:
            return self
        raise ValueError("target must be a ComponentId, AttributeId, or PythonBuiltinType")