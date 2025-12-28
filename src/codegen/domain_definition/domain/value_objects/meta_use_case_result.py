from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.shared.models import ValueObject




class MetaUseCaseResult(ValueObject):
    """Specification of a use case result to be generated."""
    
    name: str = Field(default_factory=str)
    attributes: list[Attribute] = Field(default_factory=list)
    
      

