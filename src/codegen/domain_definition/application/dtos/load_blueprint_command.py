from pydantic import BaseModel, Field


class LoadBlueprintCommand(BaseModel):
    node: str | None = Field(default=None)
