from abc import ABC
from pathlib import Path
from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType


class ComponentPolicy(ABC):
    component_type: ClassVar[ComponentType]

    @property
    def target_path(self) -> Path:
        return Path(self.component_type.layer) / Path(self.component_type.dir_name)
