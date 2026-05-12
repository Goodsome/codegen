from pydantic import BaseModel, Field
from typing import Union


class GenerateProjectCommand(BaseModel):
    nodes: list[str] | None = Field(default=None)
    generate_tests: bool = Field(default_factory=False)
