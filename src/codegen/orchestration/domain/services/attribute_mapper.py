from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.domain_definition.domain.value_objects.attribute import Attribute




@dataclass 
class AttributeMapper:
    
    
    
      
    def to_parameter_spec(
        self, 
        attribute: Attribute 
    ) -> ParameterSpec:
        ...
         
      
    def to_attribute(
        self, 
        parameter_spec: ParameterSpec 
    ) -> Attribute:
        ...
         
      

