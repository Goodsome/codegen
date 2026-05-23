from dataclasses import dataclass
import re
from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.component_dir import ComponentDir


@dataclass
class ImportParser:

    dir_to_type_registry: dict[ComponentDir, ComponentType]

    PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"codegen\.(?P<context>[^.]+)\.(?P<layer>[^.]+)\.(?P<dir>[^.]+)\.(?P<name>[^.\s]+)")

    
    def parse(self, import_module: str) -> tuple[str, ComponentType]:
        match = self.PATTERN.search(import_module)
        if not match:
            return import_module, ComponentType.EXTERNAL

        groups = match.groupdict()
        context = groups["context"]
        dir_str = groups["dir"]
        
        component_dir = ComponentDir(dir_str)
        component_type = self.dir_to_type_registry.get(component_dir, ComponentType.EXTERNAL)
        return context, component_type