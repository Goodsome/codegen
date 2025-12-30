from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.meta_implementation import MetaImplementation
from dataclasses import dataclass




@dataclass 
class ImplementationMapper:
    
    
    attribute_mapper: AttributeMapper
    method_mapper: MethodMapper
    
      
    def to_module_spec(
        self, 
        implementation: MetaImplementation 
    ) -> ModuleSpec:
        ...
         
      
    def to_implementation(
        self, 
        module_spec: ModuleSpec 
    ) -> MetaImplementation:
        ...
         
      

