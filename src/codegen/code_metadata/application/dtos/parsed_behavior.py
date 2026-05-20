from pydantic import BaseModel

from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_type import ParsedType


class ParsedBehavior(BaseModel):
    name: str
    description: str | None
    inputs: list[ParsedAttribute]
    output: ParsedType
    