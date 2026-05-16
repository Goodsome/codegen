
from pathlib import Path
from pydantic import BaseModel


class ParsedComponent(BaseModel):
    name: str
    description: str
    path: Path
