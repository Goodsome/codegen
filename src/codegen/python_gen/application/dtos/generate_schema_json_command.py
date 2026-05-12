from pydantic import BaseModel, Field
from typing import Union


class GenerateSchemaJsonCommand(BaseModel):
    schema_: str | None = Field(default=None)
