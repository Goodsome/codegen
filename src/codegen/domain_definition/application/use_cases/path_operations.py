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


# ============================================================================
# SetValue Use Case
# ============================================================================

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


# ============================================================================
# RemoveValue Use Case
# ============================================================================

@dataclass(frozen=True)
class RemoveValueCommand:
    """Command to remove a value at a path."""
    path: str


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
    
    def execute(self, cmd: RemoveValueCommand) -> None:
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
