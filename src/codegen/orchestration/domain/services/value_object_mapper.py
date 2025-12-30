from codegen.domain_definition.domain.value_objects.meta_value_object import MetaValueObject
from dataclasses import dataclass
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec




@dataclass 
class ValueObjectMapper:
    
    
    attribute_mapper: AttributeMapper
    method_mapper: MethodMapper
    
      
    def to_module_spec(
        self, 
        value_object: MetaValueObject 
    ) -> ModuleSpec:
        ...
         
      
    def to_value_object(
        self, 
        module_spec: ModuleSpec 
    ) -> MetaValueObject:
        ...
         
      

