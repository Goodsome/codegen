from pydantic import BaseModel, Field


class UpsertComponentCommand(BaseModel):
    type: str
    name: str
    description: str
    context: str

    bases: list[str] = Field(default_factory=list)
