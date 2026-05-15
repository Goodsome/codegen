from pydantic import BaseModel, Field


class UpdateComponentCommand(BaseModel):
    id: str
    type: str | None = None
    name: str | None = Field(default=None)
    description: str | None = None
    context: str | None = None
