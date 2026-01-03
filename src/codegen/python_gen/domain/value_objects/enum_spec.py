from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.python_gen.domain.value_objects.enum_member_spec import EnumMemberSpec




class EnumSpec(ValueObject):
    """Represents an enum in a Python module."""
    
    name: str
    description: str = Field(default_factory=str)
    decorators: list[str] = Field(default_factory=list)
    base_class: str = Field(default_factory=str)
    members: list[EnumMemberSpec] = Field(default_factory=list)
    
      

