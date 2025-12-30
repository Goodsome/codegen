from dataclasses import dataclass
from codegen.domain_definition.domain.value_objects.meta_port import MetaPort
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec




@dataclass 
class PortMapper:
    
    
    attribute_mapper: AttributeMapper
    method_mapper: MethodMapper
    
      
    def to_module_spec(
        self, 
        port: MetaPort 
    ) -> ModuleSpec:
        ...
         
      
    def to_port(
        self, 
        module_spec: ModuleSpec 
    ) -> MetaPort:
        ...
         
      

