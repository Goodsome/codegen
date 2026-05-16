
from pydantic import BaseModel


class ParsedComponent(BaseModel):
    name: str
    description: str
