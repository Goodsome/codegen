from codegen.domain_definition.domain.value_objects.meta_value_object import MetaValueObject
from codegen.domain_definition.domain.value_objects.meta_port import MetaPort
from codegen.domain_definition.domain.value_objects.meta_service import MetaService
from codegen.domain_definition.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.domain_definition.domain.value_objects.meta_enum import MetaEnum
from pydantic import Field
from codegen.shared.models import ValueObject




class MetaDomain(ValueObject):
    """Specification of a domain to be generated."""
    
    aggregates: list[MetaAggregate] = Field(default_factory=list)
    enums: list[MetaEnum] = Field(default_factory=list)
    value_objects: list[MetaValueObject] = Field(default_factory=list)
    services: list[MetaService] = Field(default_factory=list)
    ports: list[MetaPort] = Field(default_factory=list)
    
      

