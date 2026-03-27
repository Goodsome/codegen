from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from dataclasses import dataclass
from codegen.domain_definition.domain.services.blueprint_path_operations import (
    BlueprintPathOperations,
)


@dataclass(frozen=True)
class RemoveValueCommand:
    """Command to remove a value at a path."""
    path: str


@dataclass(frozen=True)
class RemoveValueResult:
    """Result of a remove value operation."""
    blueprint: dict | None


@dataclass
class RemoveValue:
    """
    Use case to remove a value from Blueprint at the specified path.
    
    Supports:
    - Removing fields: "contexts.sales.description" (sets to None)
    - Removing list items: "contexts[0]" or "contexts.sales" (removes from list)
    """
    storage: BlueprintStorage
    operations: BlueprintPathOperations
    
    def execute(self, cmd: RemoveValueCommand) -> RemoveValueResult:
        """
        Execute the remove value command.
        
        Args:
            cmd: Command containing the path to remove
            
        Raises:
            ValueError: If blueprint not found or path invalid
            KeyError: If path not found
        """
        blueprint = self.storage.load()
        if not blueprint:
            raise ValueError("Blueprint not found")
        
        new_blueprint = self.operations.remove_value(blueprint, cmd.path)
        
        self.storage.save(new_blueprint)
        return RemoveValueResult(blueprint=new_blueprint)
