from typing import Union
from codegen.shared.models import ValueObject
from pydantic import Field




class EnumMemberSpec(ValueObject):
    """Represents an enum member in a Python module."""
    
    name: str
    value: str | int | None = Field(default=None)
    description: str = Field(default_factory=str)
    
      

