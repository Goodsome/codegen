from codegen.code_metadata.domain.value_objects.scenario import Scenario
from codegen.code_metadata.application.dtos.type_def_dto import TypeDefDTO
from pydantic import BaseModel
from codegen.code_metadata.application.dtos.attribute_dto import AttributeDTO


class BehaviorDTO(BaseModel):
    name: str
    description: str
    scenarios: list[Scenario]
    inputs: list[AttributeDTO]
    output: TypeDefDTO
