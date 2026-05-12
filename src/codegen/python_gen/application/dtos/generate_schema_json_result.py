from pydantic import BaseModel, Field


class GenerateSchemaJsonResult(BaseModel):
    result: str | None = Field(default=None)
