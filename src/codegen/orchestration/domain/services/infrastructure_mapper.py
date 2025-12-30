from codegen.orchestration.domain.services.implementation_mapper import ImplementationMapper
from codegen.domain_definition.domain.value_objects.meta_infrastructure import MetaInfrastructure
from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec




@dataclass 
class InfrastructureMapper:
    
    
    implementation_mapper: ImplementationMapper
    
      
    def to_package_spec(
        self, 
        infrastructure: MetaInfrastructure 
    ) -> PackageSpec:
        ...
         
      
    def to_infrastructure(
        self, 
        package_spec: PackageSpec 
    ) -> MetaInfrastructure:
        ...
         
      

