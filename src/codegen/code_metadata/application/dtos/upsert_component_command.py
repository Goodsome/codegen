from typing import Self

from pydantic import BaseModel, Field

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent


class UpsertComponentCommand(BaseModel):
    type: str
    name: str
    description: str
    context: str

    bases: list[str] = Field(default_factory=list)
    imported_components: list[ImportedComponent] = Field(default_factory=list)

    def get_upsert_imported_components(self) -> list[Self]:
        return [
            self.__class__(
                type=ic.type,
                name=ic.name,
                description="",
                context=ic.context,
            )
            for ic in self.imported_components
        ]
