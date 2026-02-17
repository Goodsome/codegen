"""
Path-based Use Cases for Blueprint manipulation.

Provides GetValue, SetValue, RemoveValue use cases that operate
on Blueprint using path expressions.
"""

from dataclasses import dataclass
from typing import Any

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.services.blueprint_path_operations import (
    BlueprintPathOperations,
)


# ============================================================================
# GetValue Use Case
# ============================================================================

@dataclass(frozen=True)
class GetValueCommand:
    """Command to get a value at a path."""
    path: str


@dataclass
class GetValue:
    """
    Use case to get a value from Blueprint at the specified path.
    """
    storage: BlueprintStorage
    operations: BlueprintPathOperations
    
    def execute(self, cmd: GetValueCommand) -> Any:
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

