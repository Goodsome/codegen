from typing import Union
from codegen.shared.models import ValueObject
from pydantic import Field




class MetaEnumMember(ValueObject):
    """Specification of an enum member to be generated."""
    
    name: str
    value: str | int | None = Field(default=None)
    description: str = Field(default_factory=str)
    
      

