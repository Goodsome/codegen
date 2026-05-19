from pydantic import BaseModel

from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.parsed_type import ParsedType


class ParsedAttribute(BaseModel):
    name: str
    description: str
    type: ParsedType | None
    value: ParsedExpr | None
    