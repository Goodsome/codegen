from abc import ABC
from pathlib import Path
from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.shared.domain.value_objects.snake_string import SnakeString


class ComponentPolicy(ABC):
    component_type: ClassVar[ComponentType]
    dir_name: ClassVar[ComponentDir]
    layer: ClassVar[ArchitectureLayer]

    @property
    def target_path(self) -> Path:
        return Path(self.layer) / Path(self.dir_name)

    def get_import_module(self, context: str, component_name: str) -> str:
        return f"codegen.{context}.{self.layer}.{self.dir_name}.{SnakeString(component_name)}"
        
    def get_target_path(self, context: str) -> Path:
        p = Path(f"src/codegen/{context}") / Path(self.layer) / Path(self.dir_name)
        return p