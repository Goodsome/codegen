import json
from pathlib import Path
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from dataclasses import dataclass
from codegen.python_gen.application.dtos.generate_schema_json_command import (
    GenerateSchemaJsonCommand,
)
from codegen.python_gen.application.dtos.generate_schema_json_result import (
    GenerateSchemaJsonResult,
)
from typing import Self


@dataclass
class GenerateSchemaJson:
    file_system_port: FileSystemPort

    def execute(self: Self, cmd: GenerateSchemaJsonCommand) -> GenerateSchemaJsonResult:
        json_schema = Blueprint.model_json_schema()
        content = json.dumps(
            json_schema, indent=2, sort_keys=True, separators=(",", ":")
        )
        self.file_system_port.write_file(
            path=Path("codegen.schema.json"), content=content, overwrite=True
        )
        return GenerateSchemaJsonResult()
