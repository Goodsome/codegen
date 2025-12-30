from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.port_binding import PortBinding




class MetaBootstrap(ValueObject):
    """Specification of the bootstrap configuration."""
    
    bindings: list[PortBinding] = Field(default_factory=list)
    
      

