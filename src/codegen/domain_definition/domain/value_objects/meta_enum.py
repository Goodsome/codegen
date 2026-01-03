from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.domain_definition.domain.value_objects.meta_enum_member import MetaEnumMember




class MetaEnum(ValueObject):
    """Specification of an enum to be generated."""
    
    name: str
    description: str = Field(default_factory=str)
    members: list[MetaEnumMember]
    
      

