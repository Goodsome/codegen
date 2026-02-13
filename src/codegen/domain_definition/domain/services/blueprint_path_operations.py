"""
Blueprint Path Operations - Get, Set, and Remove values in Blueprint using path expressions.

This service builds on BlueprintPathResolver to provide CRUD operations
on Blueprint models using path expressions.
"""

import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from codegen.domain_definition.domain.services.blueprint_path_resolver import (
    BlueprintPathResolver,
    PathSegment,
)


@dataclass
class BlueprintPathOperations:
    """
    Provides get/set/remove operations on Blueprint using path expressions.
    
    Uses Pydantic's model_copy for immutable updates.
    """
    
    resolver: BlueprintPathResolver
    
    def get_value(self, obj: Any, path: str) -> Any:
        """
        Get a value at the specified path.
        
        Args:
            obj: The root object (Blueprint)
            path: Path expression
            
        Returns:
            The value at the path
        """
        return self.resolver.resolve(obj, path)
    
    def set_value(self, obj: Any, path: str, value: Any, append: bool = False) -> Any:
        """
        Set a value at the specified path, returning a new object.
        
        Args:
            obj: The root object (Blueprint)
            path: Path expression
            value: The value to set
            append: If True and target is a list, append value instead of replace
            
        Returns:
            A new object with the value set
        """
        segments = self.resolver.parse(path)
        if not segments:
            raise ValueError("Empty path")
        
        return self._set_recursive(obj, segments, value, append)
    
    def remove_value(self, obj: Any, path: str) -> Any:
        """
        Remove a value at the specified path, returning a new object.
        
        Args:
            obj: The root object (Blueprint)
            path: Path expression
            
        Returns:
            A new object with the value removed
        """
        segments = self.resolver.parse(path)
        if not segments:
            raise ValueError("Empty path")
        
        return self._remove_recursive(obj, segments)
    
    def _set_recursive(
        self, obj: Any, segments: list[PathSegment], value: Any, append: bool
    ) -> Any:
        """Recursively navigate and set value."""
        if not segments:
            return value
        
        segment = segments[0]
        remaining = segments[1:]
        
        # Last segment - set the value
        if not remaining:
            return self._set_final_value(obj, segment, value, append)
        
        # Intermediate segment - navigate and recurse
        current_value = self._get_segment_value(obj, segment)
        new_value = self._set_recursive(current_value, remaining, value, append)
        return self._update_segment(obj, segment, new_value)
    
    def _remove_recursive(self, obj: Any, segments: list[PathSegment]) -> Any:
        """Recursively navigate and remove value."""
        if not segments:
            raise ValueError("Cannot remove root")
        
        segment = segments[0]
        remaining = segments[1:]
        
        # Last segment - remove the value
        if not remaining:
            return self._remove_final_value(obj, segment)
        
        # Intermediate segment - navigate and recurse
        current_value = self._get_segment_value(obj, segment)
        new_value = self._remove_recursive(current_value, remaining)
        return self._update_segment(obj, segment, new_value)
    
    def _get_segment_value(self, obj: Any, segment: PathSegment) -> Any:
        """Get value for a segment (delegate to resolver logic)."""
        current = obj
        
        if segment.name:
            current = self._access_by_name(current, segment.name)
        
        if segment.index is not None:
            current = current[segment.index]
        
        return current
    
    def _access_by_name(self, obj: Any, name: str) -> Any:
        """Access by name - mirrors resolver logic."""
        if hasattr(obj, name):
            return getattr(obj, name)
        if isinstance(obj, dict):
            return obj[name]
        if isinstance(obj, (list, tuple)):
            for item in obj:
                item_name = self._get_item_name(item)
                if item_name and str(item_name) == name:
                    return item
            raise KeyError(f"No item with name '{name}' found in list")
        raise KeyError(f"Cannot access '{name}' on {type(obj)}")
    
    def _get_item_name(self, item: Any) -> str | None:
        """Get name field from item."""
        if hasattr(item, 'name'):
            name_val = getattr(item, 'name')
            return str(name_val) if name_val is not None else None
        if isinstance(item, dict) and 'name' in item:
            return str(item['name'])
        return None
    
    def _find_item_index(self, items: list, name: str) -> int:
        """Find index of item with matching name."""
        for i, item in enumerate(items):
            item_name = self._get_item_name(item)
            if item_name and str(item_name) == name:
                return i
        raise KeyError(f"No item with name '{name}' found")
    
    def _set_final_value(
        self, obj: Any, segment: PathSegment, value: Any, append: bool
    ) -> Any:
        """Set value at the final segment."""
        if segment.index is not None:
            # Setting into a list by index
            target = self._access_by_name(obj, segment.name) if segment.name else obj
            if append:
                new_list = list(target) + [value]
            else:
                new_list = list(target)
                new_list[segment.index] = value
            
            if segment.name:
                return self._update_field(obj, segment.name, new_list)
            return new_list
        
        if segment.name:
            # Check if target is a list - handle append or upsert by name
            if hasattr(obj, segment.name):
                current = getattr(obj, segment.name)
                if isinstance(current, list) and append:
                    new_list = list(current) + [value]
                    return self._update_field(obj, segment.name, new_list)
            
            return self._update_field(obj, segment.name, value)
        
        raise ValueError("Invalid segment for set operation")
    
    def _remove_final_value(self, obj: Any, segment: PathSegment) -> Any:
        """Remove value at the final segment."""
        if segment.index is not None:
            # Remove from list by index
            target = self._access_by_name(obj, segment.name) if segment.name else obj
            new_list = [item for i, item in enumerate(target) if i != segment.index]
            
            if segment.name:
                return self._update_field(obj, segment.name, new_list)
            return new_list
        
        if segment.name:
            # Check if we're removing from a list by name
            if hasattr(obj, segment.name):
                return self._update_field(obj, segment.name, None)
            
            # Maybe we're removing an item from a parent list by name
            if isinstance(obj, list):
                return [item for item in obj if self._get_item_name(item) != segment.name]
            
            raise KeyError(f"Cannot remove '{segment.name}' from {type(obj)}")
        
        raise ValueError("Invalid segment for remove operation")
    
    def _update_segment(self, obj: Any, segment: PathSegment, new_value: Any) -> Any:
        """Update a segment in the path with new value."""
        if segment.index is not None:
            # Update list item by index
            target = self._access_by_name(obj, segment.name) if segment.name else obj
            new_list = list(target)
            new_list[segment.index] = new_value
            
            if segment.name:
                return self._update_field(obj, segment.name, new_list)
            return new_list
        
        if segment.name:
            # Check if it's a named item in a list
            if isinstance(obj, list):
                idx = self._find_item_index(obj, segment.name)
                new_list = list(obj)
                new_list[idx] = new_value
                return new_list
            
            return self._update_field(obj, segment.name, new_value)
        
        return new_value
    
    def _update_field(self, obj: Any, field_name: str, new_value: Any) -> Any:
        """Update a field on an object, returning new object."""
        if isinstance(obj, BaseModel):
            return obj.model_copy(update={field_name: new_value})
        if isinstance(obj, dict):
            new_dict = dict(obj)
            new_dict[field_name] = new_value
            return new_dict
        if hasattr(obj, '__dict__'):
            # Generic object - create copy
            import copy
            new_obj = copy.copy(obj)
            setattr(new_obj, field_name, new_value)
            return new_obj
        
        raise TypeError(f"Cannot update field on {type(obj)}")
    
    def parse_value(self, value_str: str) -> Any:
        """
        Parse a value string into appropriate Python type.
        Tries JSON first, falls back to string.
        """
        if not value_str:
            return value_str
        
        # Try JSON parsing
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            # Return as string
            return value_str
