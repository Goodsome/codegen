from pydantic import BaseModel
from codegen.code_metadata.application.dtos.type_def_dto import TypeDefDTO


class AttributeDTO(BaseModel):
    name: str
    description: str
    type: TypeDefDTO
