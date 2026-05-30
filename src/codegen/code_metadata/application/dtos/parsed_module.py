
from pathlib import Path
from typing import Annotated, Literal
from pydantic import BaseModel, Field

from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.domain.enums.module_kind import ModuleKind


class ParsedFileModule(BaseModel):
    kind: Literal[ModuleKind.FILE] = ModuleKind.FILE

    name: str
    path: Path
    
    components: list[ParsedComponent]
    dependencies: list[ImportDto]

    @property
    def import_path(self) -> str:
        root_path = Path("src")
        relative_path = self.path.relative_to(root_path)
        parts = relative_path.with_suffix("").parts
        return ".".join(parts)


class ParsedDirectoryModule(BaseModel):
    kind: Literal[ModuleKind.DIRECTORY] = ModuleKind.DIRECTORY

    name: str
    path: Path
    
    public_component_names: list[str]
    
    @property
    def import_path(self) -> str:
        root_path = Path("src")
        relative_path = self.path.relative_to(root_path)
        parts = relative_path.parts
        return ".".join(parts)


class ParsedExternalModule(BaseModel):
    kind: Literal[ModuleKind.EXTERNAL] = ModuleKind.EXTERNAL
    name: str
    components: list[str]

    @property
    def import_path(self) -> str:
        return self.name


ParsedModule = Annotated[
    ParsedFileModule | ParsedDirectoryModule | ParsedExternalModule,
    Field(discriminator="kind"),
]
