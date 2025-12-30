import re
from dataclasses import dataclass


@dataclass
class NamingService:
    """Provides naming conventions for generated artifacts."""

    def to_snake_case(self, name: str) -> str:
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower().replace("-", "_")
