"""
Blueprint Path Resolver - Parse and resolve path expressions for Blueprint navigation.

Supports paths like:
- "project.version" - simple dot notation
- "contexts[0].name" - list index access
- "contexts.sales.aggregates.Order" - dict key access by name
"""

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class PathSegment:
    """Represents a single segment in a path expression."""
    name: str
    index: int | None = None  # None = dict key by name, int = list index
    
    def is_index_access(self) -> bool:
        return self.index is not None


class BlueprintPathResolver:
    """
    Parses path expressions and resolves them against Blueprint/Pydantic models.
    
    Path syntax:
    - Dot notation: "contexts.sales" 
    - Index notation: "contexts[0]"
    - Mixed: "contexts[0].aggregates.Order"
    - Field access by name in list: "contexts.DomainDefinition" (finds by 'name' field)
    """
    
    # Pattern matches: name, name[index], or [index]
    _SEGMENT_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)?(?:\[(\d+)\])?')
    
    def parse(self, path: str) -> list[PathSegment]:
        """
        Parse a path string into a list of PathSegments.
        
        Examples:
            "project.version" -> [PathSegment("project"), PathSegment("version")]
            "contexts[0]" -> [PathSegment("contexts", 0)]
            "contexts.sales" -> [PathSegment("contexts"), PathSegment("sales")]
        """
        if not path or not path.strip():
            return []
        
        segments: list[PathSegment] = []
        parts = path.split('.')
        
        for part in parts:
            if not part:
                continue
            
            # Check for index notation: name[index] or just [index]
            if '[' in part:
                # Parse: name[0] or [0]
                match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)?\[(\d+)\]$', part)
                if match:
                    name = match.group(1) or ''
                    index = int(match.group(2))
                    if name:
                        # name[index] - first access name, then index
                        segments.append(PathSegment(name=name, index=index))
                    else:
                        # [index] only - just index access
                        segments.append(PathSegment(name='', index=index))
                else:
                    raise ValueError(f"Invalid path segment: {part}")
            else:
                # Simple name segment
                segments.append(PathSegment(name=part))
        
        return segments
    
    def resolve(self, obj: Any, path: str) -> Any:
        """
        Resolve a path against an object and return the value.
        
        Args:
            obj: The root object (Blueprint or any nested object)
            path: The path expression
            
        Returns:
            The value at the specified path
            
        Raises:
            KeyError: If path segment not found
            IndexError: If index out of range
        """
        segments = self.parse(path)
        return self._resolve_segments(obj, segments)
    
    def _resolve_segments(self, obj: Any, segments: list[PathSegment]) -> Any:
        """Recursively resolve path segments."""
        if not segments:
            return obj
        
        segment = segments[0]
        remaining = segments[1:]
        
        # Get the next value based on segment type
        next_obj = self._get_segment_value(obj, segment)
        
        return self._resolve_segments(next_obj, remaining)
    
    def _get_segment_value(self, obj: Any, segment: PathSegment) -> Any:
        """Get value for a single path segment."""
        current = obj
        
        # First, access by name if present
        if segment.name:
            current = self._access_by_name(current, segment.name)
        
        # Then, access by index if present
        if segment.index is not None:
            if isinstance(current, (list, tuple)):
                if segment.index >= len(current):
                    raise IndexError(f"Index {segment.index} out of range for list of length {len(current)}")
                current = current[segment.index]
            else:
                raise TypeError(f"Cannot index into non-list type: {type(current)}")
        
        return current
    
    def _access_by_name(self, obj: Any, name: str) -> Any:
        """
        Access an attribute or dict key by name.
        For lists, searches for item with matching 'name' field.
        """
        # Pydantic model or object with attribute
        if hasattr(obj, name):
            return getattr(obj, name)
        
        # Dict access
        if isinstance(obj, dict):
            if name in obj:
                return obj[name]
            raise KeyError(f"Key '{name}' not found in dict")
        
        # List - search for item with matching 'name' field
        if isinstance(obj, (list, tuple)):
            for item in obj:
                item_name = self._get_item_name(item)
                if item_name and str(item_name) == name:
                    return item
            raise KeyError(f"No item with name '{name}' found in list")
        
        raise KeyError(f"Cannot access '{name}' on {type(obj)}")
    
    def _get_item_name(self, item: Any) -> str | None:
        """Get the 'name' field value from an item, if it exists."""
        if hasattr(item, 'name'):
            name_val = getattr(item, 'name')
            # Handle PascalString or similar wrapper types
            return str(name_val) if name_val is not None else None
        if isinstance(item, dict) and 'name' in item:
            return str(item['name'])
        return None
