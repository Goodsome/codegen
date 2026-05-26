from pydantic import BaseModel
from typing import Any


class ComponentDto(BaseModel):
    id: str
    kind: str
    type: str
    name: str
    description: str
    context: str
    layer: str
