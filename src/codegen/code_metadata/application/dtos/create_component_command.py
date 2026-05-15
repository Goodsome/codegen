
from pydantic import BaseModel


class CreateComponentCommand(BaseModel):
    type: str
    name: str
    description: str
    context: str
