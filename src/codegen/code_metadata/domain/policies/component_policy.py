from abc import ABC
from pathlib import Path
from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_dir import ComponentDir


class ComponentPolicy(ABC):
    component_type: ClassVar[ComponentType]
    dir_name: ClassVar[ComponentDir]
    layer: ClassVar[ArchitectureLayer]

    def get_target_path(self, context: str) -> Path:
        p = Path(f"src/codegen/{context}") / Path(self.layer) / Path(self.dir_name)
        return p

    def get_dir_name(self):
        return self.dir_name