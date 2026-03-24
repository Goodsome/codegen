from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from dataclasses import dataclass
from pydantic import BaseModel


class UpsertContextCommand(BaseModel):
    name: str
    description: str


class UpsertContextResult(BaseModel): ...


@dataclass
class UpsertContext:
    storage: BlueprintStorage

    def execute(self, cmd: UpsertContextCommand) -> UpsertContextResult: ...
