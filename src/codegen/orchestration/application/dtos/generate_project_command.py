from pydantic import BaseModel, Field


class GenerateProjectCommand(BaseModel):
    nodes: list[str] | None = Field(default=None)
    generate_tests: bool = Field(default=False)
