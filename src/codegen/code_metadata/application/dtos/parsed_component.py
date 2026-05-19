from pydantic import BaseModel, Field

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_type import ParsedType


class ParsedComponent(BaseModel):
    name: str
    description: str

    attributes: list[ParsedAttribute] = Field(default_factory=list)
    
    bases: list[ParsedType] = Field(default_factory=list)
