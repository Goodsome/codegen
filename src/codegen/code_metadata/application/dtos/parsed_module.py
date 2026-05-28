
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
    
    component_names: list[ParsedComponent]
    dependencies: list[ImportDto]


class ParsedDirectoryModule(BaseModel):
    kind: Literal[ModuleKind.DIRECTORY] = ModuleKind.DIRECTORY

    name: str
    path: Path
    
    public_component_names: list[str]


class ParsedExternalModule(BaseModel):
    kind: Literal[ModuleKind.EXTERNAL] = ModuleKind.EXTERNAL
    name: str
    components: list[str]


ParsedModule = Annotated[
    ParsedFileModule | ParsedDirectoryModule | ParsedExternalModule,
    Field(discriminator="kind"),
]
