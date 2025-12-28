from codegen.domain_definition.domain.value_objects.meta_use_case_result import MetaUseCaseResult
from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.domain_definition.domain.value_objects.meta_use_case_query import MetaUseCaseQuery
from codegen.domain_definition.domain.value_objects.meta_use_case_command import MetaUseCaseCommand




class MetaUseCase(ValueObject):
    """Specification of a use case to be generated."""
    
    name: str
    kind: str
    attributes: list[Attribute] = Field(default_factory=list)
    description: str = Field(default_factory=str)
    command: MetaUseCaseCommand = Field(default_factory=MetaUseCaseCommand)
    query: MetaUseCaseQuery = Field(default_factory=MetaUseCaseQuery)
    result: MetaUseCaseResult = Field(default_factory=MetaUseCaseResult)
    
      

