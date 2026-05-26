from typing import Annotated, Literal

from pydantic import Field

from codegen.code_metadata.domain.enums.module_kind import ModuleKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class FileModule(AggregateRoot[ModuleId]):
    kind: Literal[ModuleKind.FILE] = ModuleKind.FILE

    name: str
    components: list[ComponentId]
    dependencies: list[ComponentId]


class DirectoryModule(AggregateRoot[ModuleId]):
    kind: Literal[ModuleKind.DIRECTORY] = ModuleKind.DIRECTORY

    name: str
    modules: list[ModuleId]
    public_api: list[ComponentId]


class ExternalModule(AggregateRoot[ModuleId]):
    kind: Literal[ModuleKind.EXTERNAL] = ModuleKind.EXTERNAL

    name: str
    components: list[ComponentId]


Module = Annotated[
    FileModule | DirectoryModule | ExternalModule,
    Field(discriminator="kind"),
]
