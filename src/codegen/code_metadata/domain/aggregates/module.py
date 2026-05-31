from __future__ import annotations
from collections.abc import Iterator
from typing import Annotated, Literal, Self, override

from pydantic import Field

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums.module_kind import ModuleKind
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.value_objects.module_dependency import (
    ModuleDependency,
)
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class BaseModule(AggregateRoot[ModuleId]):
    name: str
    path: str

    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        yield from []
    
    def collect_raw_reference_targets(self) -> Iterator[ReferenceTarget]:
        for reference_target in self.iter_reference_targets():
            if reference_target.is_resolved:
                continue
            yield reference_target
            
    def resolve(
        self,
        map: dict[str, ReferenceTarget],
    ) -> Self:
        for reference_target in self.iter_reference_targets():
            reference_target.resolve(map)
        return self


class FileModule(BaseModule):
    kind: Literal[ModuleKind.FILE] = ModuleKind.FILE

    components: list[Component]
    dependencies: list[ModuleDependency]

    dir_module_id: ModuleId | None

    def find_component(self, name: str) -> Component | None:
        for component in self.components:
            if component.name == name:
                return component
        return None

    @override
    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        for component in self.components:
            yield from component.iter_reference_targets()
        for dependency in self.dependencies:
            yield from dependency.iter_reference_targets()

    def bind_dir_module_id(self, dir_module_id: ModuleId) -> None:
        self.dir_module_id = dir_module_id

class DirectoryModule(BaseModule):
    kind: Literal[ModuleKind.DIRECTORY] = ModuleKind.DIRECTORY

    public_component_ids: list[ReferenceTarget]
    
    sub_module_ids: list[ModuleId]
    dir_module_id: ModuleId | None
    
    @override
    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        yield from self.public_component_ids


    def bind_sub_module_id(self, sub_module_id: ModuleId) -> None:
        if sub_module_id in self.sub_module_ids:
            return
        self.sub_module_ids.append(sub_module_id)

    def bind_dir_module_id(self, dir_module_id: ModuleId) -> None:
        self.dir_module_id = dir_module_id

class ExternalModule(BaseModule):
    kind: Literal[ModuleKind.EXTERNAL] = ModuleKind.EXTERNAL
    components: list[Component]

    def find_component(self, name: str) -> Component | None:
        for component in self.components:
            if component.name == name:
                return component
        return None


Module = Annotated[
    FileModule | DirectoryModule | ExternalModule,
    Field(discriminator="kind"),
]
