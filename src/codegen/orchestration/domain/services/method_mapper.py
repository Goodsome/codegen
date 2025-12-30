from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from dataclasses import dataclass




@dataclass 
class MethodMapper:
    
    
    attribute_mapper: AttributeMapper
    
      
    def to_function_spec(
        self, 
        method: MethodSpec 
    ) -> FunctionSpec:
        ...
         
      
    def to_method(
        self, 
        function_spec: FunctionSpec 
    ) -> MethodSpec:
        ...
         
      

