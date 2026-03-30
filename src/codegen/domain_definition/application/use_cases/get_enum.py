from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.enum_spec import EnumSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetEnumQuery(BaseModel):
    context_name: str
    name: str


class GetEnumResult(BaseModel):
    enum: EnumSpec


@dataclass
class GetEnum:
    storage: BlueprintStorage

    def execute(self, query: GetEnumQuery) -> GetEnumResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        enum = context.domain.get_enum(query.name)

        return GetEnumResult(enum=enum)
