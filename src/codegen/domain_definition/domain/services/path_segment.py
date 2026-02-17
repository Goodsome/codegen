from dataclasses import field, dataclass
from typing import Union


@dataclass
class PathSegment:
    """Represents a single segment in a path expression."""
    name: str
    index: int | None = None  # None = dict key by name, int = list index
    
    def is_index_access(self) -> bool:
        return self.index is not None
