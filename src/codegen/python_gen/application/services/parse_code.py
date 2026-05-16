from dataclasses import dataclass
from pathlib import Path

from codegen.python_gen.domain.ports.source_code_port import SourceCodePort
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class ParseCode:

    source_code_port: SourceCodePort
    file_system_port: FileSystemPort

    def execute(self, code_path: Path) -> ModuleSpec:
        if not self.file_system_port.is_file(code_path):
            raise ValueError(f"{code_path} is not file")
        if code_path.suffix != ".py":
            raise ValueError(f"{code_path} is not a Python file")
        source_code = self.file_system_port.read_file(code_path)
        module_name = code_path.stem
        module_spec = self.source_code_port.parse_module(source_code, module_name)
        return module_spec