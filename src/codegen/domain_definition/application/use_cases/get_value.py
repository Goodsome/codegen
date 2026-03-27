from codegen.domain_definition.domain.services.blueprint_path_operations import (
    BlueprintPathOperations,
)
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from dataclasses import dataclass
from pydantic import BaseModel


class GetValueCommand(BaseModel):
    path: str


class GetValueResult(BaseModel): ...


@dataclass
class GetValue:
    storage: BlueprintStorage
    operations: BlueprintPathOperations
    
    def execute(self, cmd: GetValueCommand) -> GetValueResult:
        """
        Execute the get value command.
        
        Args:
            cmd: Command containing the path to query
            
        Returns:
            The value at the specified path
            
        Raises:
            ValueError: If blueprint not found
            KeyError: If path not found
        """
        blueprint = self.storage.load()
        if not blueprint:
            raise ValueError("Blueprint not found")
        
        return self.operations.get_value(blueprint, cmd.path)

