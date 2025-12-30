from codegen.orchestration.domain.services.method_mapper import MethodMapper
from dataclasses import dataclass
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.meta_use_case import MetaUseCase




@dataclass 
class UseCaseMapper:
    
    
    attribute_mapper: AttributeMapper
    method_mapper: MethodMapper
    
      
    def to_module_spec(
        self, 
        use_case: MetaUseCase 
    ) -> ModuleSpec:
        ...
         
      
    def to_use_case(
        self, 
        module_spec: ModuleSpec 
    ) -> MetaUseCase:
        ...
         
      

