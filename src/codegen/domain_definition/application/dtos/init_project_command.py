from pydantic import BaseModel, Field
from typing import Union


class InitProjectCommand(BaseModel):
    project_name: str | None = Field(default=None)
    project_description: str | None = Field(default=None)
