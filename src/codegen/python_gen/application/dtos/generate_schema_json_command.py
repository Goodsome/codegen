from pydantic import BaseModel, Field


class GenerateSchemaJsonCommand(BaseModel):
    schema_: str | None = Field(default=None)
