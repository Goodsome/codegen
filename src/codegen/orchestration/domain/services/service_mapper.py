from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.meta_service import MetaService
from dataclasses import dataclass
from codegen.orchestration.domain.services.method_mapper import MethodMapper




@dataclass 
class ServiceMapper:
    
    
    attribute_mapper: AttributeMapper
    method_mapper: MethodMapper
    
      
    def to_module_spec(
        self, 
        service: MetaService 
    ) -> ModuleSpec:
        ...
         
      
    def to_service(
        self, 
        module_spec: ModuleSpec 
    ) -> MetaService:
        ...
         
      

