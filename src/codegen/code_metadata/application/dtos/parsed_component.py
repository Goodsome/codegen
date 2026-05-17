from pydantic import BaseModel, Field

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent


class ParsedComponent(BaseModel):
    name: str
    description: str
    
    bases: list[str] = Field(default_factory=list)
    imported_components: list[ImportedComponent] = Field(default_factory=list)
