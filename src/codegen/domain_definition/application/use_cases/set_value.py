from dataclasses import dataclass
from typing import Any

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.services.blueprint_path_operations import BlueprintPathOperations


@dataclass(frozen=True)
class SetValueCommand:
    """Command to set a value at a path."""
    path: str
    value: Any
    append: bool = False  # If True, append to list instead of replace


@dataclass
class SetValue:
    """
    Use case to set a value in Blueprint at the specified path.
    
    Supports:
    - Simple field updates: "project.version"
    - Nested updates: "contexts.sales.description"
    - List append with append=True
    """
    storage: BlueprintStorage
    operations: BlueprintPathOperations
    
    def execute(self, cmd: SetValueCommand) -> None:
        """
        Execute the set value command.
        
        Args:
            cmd: Command containing path, value, and append flag
            
        Raises:
            ValueError: If blueprint not found or path invalid
        """
        blueprint = self.storage.load()
        if not blueprint:
            raise ValueError("Blueprint not found")
        
        new_blueprint = self.operations.set_value(
            blueprint, 
            cmd.path, 
            cmd.value, 
            append=cmd.append
        )
        
        self.storage.save(new_blueprint)
