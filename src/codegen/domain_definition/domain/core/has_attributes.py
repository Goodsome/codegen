from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from pydantic import BaseModel, Field


class HasAttributes(BaseModel):
    """能力：拥有内部状态（属性）"""
    
    attributes: list[AttributeSpec] = Field(default_factory=list)