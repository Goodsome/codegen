from abc import ABC
from pathlib import Path
from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.shared.domain.value_objects.snake_string import SnakeString


class ComponentPolicy(ABC):
    component_type: ClassVar[ComponentType]

    @property
    def target_path(self) -> Path:
        return Path(self.component_type.layer) / Path(self.component_type.dir_name)

    def get_import_module(self, context: str, component_name: str) -> str:
        return f"codegen.{context}.{self.component_type.layer}.{self.component_type.dir_name}.{SnakeString(component_name)}"
        
    def get_target_path(self, context: str) -> Path:
        p = Path(f"src/codegen/{context}") / Path(self.component_type.layer) / Path(self.component_type.dir_name)
        return p