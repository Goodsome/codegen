from pydantic import BaseModel, Field
from typing import Union


class GenerateSchemaJsonResult(BaseModel):
    result: str | None = Field(default=None)
