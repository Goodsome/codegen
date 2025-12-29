from codegen.domain_definition.domain.value_objects.meta_port import MetaPort
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.meta_value_object import MetaValueObject
from codegen.domain_definition.domain.value_objects.meta_aggregate import MetaAggregate
from pydantic import Field
from codegen.domain_definition.domain.value_objects.meta_service import MetaService




class MetaDomain(ValueObject):
    """Specification of a domain to be generated."""
    
    aggregates: list[MetaAggregate] = Field(default_factory=list)
    value_objects: list[MetaValueObject] = Field(default_factory=list)
    services: list[MetaService] = Field(default_factory=list)
    ports: list[MetaPort] = Field(default_factory=list)
    
      

