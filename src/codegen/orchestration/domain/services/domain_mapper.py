from codegen.domain_definition.domain.value_objects.meta_domain import MetaDomain
from codegen.orchestration.domain.services.port_mapper import PortMapper
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass
from codegen.orchestration.domain.services.value_object_mapper import ValueObjectMapper
from codegen.orchestration.domain.services.service_mapper import ServiceMapper
from codegen.orchestration.domain.services.aggregate_mapper import AggregateMapper




@dataclass 
class DomainMapper:
    
    
    aggregate_mapper: AggregateMapper
    value_object_mapper: ValueObjectMapper
    service_mapper: ServiceMapper
    port_mapper: PortMapper
    
      
    def to_package_spec(
        self, 
        domain: MetaDomain 
    ) -> PackageSpec:
        ...
         
      
    def to_domain(
        self, 
        package_spec: PackageSpec 
    ) -> MetaDomain:
        ...
         
      

