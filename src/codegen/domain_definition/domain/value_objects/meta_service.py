from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import Attribute




class MetaService(ValueObject):
    """Specification of a domain service to be generated."""
    
    name: str
    description: str = Field(default_factory=str)
    attributes: list[Attribute] = Field(default_factory=list)
    operations: list[MethodSpec] = Field(default_factory=list)
    
      

