from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from codegen.code_metadata.domain.enums.module_kind import ModuleKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class BaseModule(AggregateRoot[ModuleId]):
    context: str
    name: str


class FileModule(BaseModule):
    kind: Literal[ModuleKind.FILE] = ModuleKind.FILE
    
    path: Path
    component_ids: list[ComponentId]
    dependency_ids: list[ComponentId]
    parent_dir_id: ModuleId


class DirectoryModule(BaseModule):
    kind: Literal[ModuleKind.DIRECTORY] = ModuleKind.DIRECTORY
    
    path: Path
    sub_module_ids: list[ModuleId]
    parent_dir_id: ModuleId | None
    public_component_ids: list[ComponentId]


class ExternalModule(BaseModule):
    kind: Literal[ModuleKind.EXTERNAL] = ModuleKind.EXTERNAL
    component_ids: list[ComponentId]


Module = Annotated[
    FileModule | DirectoryModule | ExternalModule,
    Field(discriminator="kind"),
]
