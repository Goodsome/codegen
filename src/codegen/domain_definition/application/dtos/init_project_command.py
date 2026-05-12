from pydantic import BaseModel, Field


class InitProjectCommand(BaseModel):
    project_name: str | None = Field(default=None)
    project_description: str | None = Field(default=None)
