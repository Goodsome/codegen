from pydantic import BaseModel, Field
from typing import Union


class LoadBlueprintCommand(BaseModel):
    node: str | None = Field(default=None)
