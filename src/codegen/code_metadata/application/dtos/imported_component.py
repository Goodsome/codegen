from typing import override
from pydantic import BaseModel


class ImportedComponent(BaseModel):
    context: str
    name: str
    type: str
    
    @override
    def __hash__(self) -> int:
        return hash((self.context, self.name, self.type))