from codegen.orchestration.domain.services.use_case_mapper import UseCaseMapper
from codegen.domain_definition.domain.value_objects.meta_application import MetaApplication
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass




@dataclass 
class ApplicationMapper:
    
    
    use_case_mapper: UseCaseMapper
    
      
    def to_package_spec(
        self, 
        application: MetaApplication 
    ) -> PackageSpec:
        ...
         
      
    def to_application(
        self, 
        package_spec: PackageSpec 
    ) -> MetaApplication:
        ...
         
      

