from codegen.domain_definition.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec




@dataclass 
class AggregateMapper:
    
    
    attribute_mapper: AttributeMapper
    method_mapper: MethodMapper
    
      
    def to_module_spec(
        self, 
        aggregate: MetaAggregate 
    ) -> ModuleSpec:
        ...
         
      
    def to_aggregate(
        self, 
        package_spec: PackageSpec 
    ) -> MetaAggregate:
        ...
         
      

