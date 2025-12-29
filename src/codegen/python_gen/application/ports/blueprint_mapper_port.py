from abc import (abstractmethod, ABC)
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint




class BlueprintMapperPort(ABC):
    """Maps a blueprint to a package."""
    
    
      
    @abstractmethod 
    def to_package_spec(
        self, 
        blueprint: Blueprint 
    ) -> PackageSpec:
        ...
         
      
    @abstractmethod 
    def to_blueprint(
        self, 
        package_spec: PackageSpec 
    ) -> Blueprint:
        ...
         
      

