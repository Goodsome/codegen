from pydantic import BaseModel, Field

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent


class UpsertComponentCommand(BaseModel):
    type: str
    name: str
    description: str
    context: str

    bases: list[str] = Field(default_factory=list)
    imported_components: list[ImportedComponent] = Field(default_factory=list)