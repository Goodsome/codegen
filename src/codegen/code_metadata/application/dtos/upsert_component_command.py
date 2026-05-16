from pydantic import BaseModel


class UpsertComponentCommand(BaseModel):
    type: str
    name: str
    description: str
    context: str
