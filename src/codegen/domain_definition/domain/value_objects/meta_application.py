from codegen.domain_definition.domain.value_objects.meta_use_case import MetaUseCase
from codegen.domain_definition.domain.value_objects.meta_port import MetaPort
from codegen.shared.models import ValueObject
from pydantic import Field




class MetaApplication(ValueObject):
    """Specification of an application to be generated."""
    
    use_cases: list[MetaUseCase] = Field(default_factory=list)
    ports: list[MetaPort] = Field(default_factory=list)
    
      

