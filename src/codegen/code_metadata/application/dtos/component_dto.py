from pydantic import BaseModel
from typing import Any


class ComponentDTO(BaseModel):
    id: str
    type: str
    name: str
    description: str
    context: str
    layer: str

    bases: list[dict[str, Any]] = []