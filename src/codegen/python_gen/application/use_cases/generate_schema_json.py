import json
from pathlib import Path

from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateSchemaJsonCommand: ...


@dataclass(frozen=True)
class GenerateSchemaJsonResult: ...


@dataclass
class GenerateSchemaJson:
    file_system_port: FileSystemPort

    def execute(self, cmd: GenerateSchemaJsonCommand) -> GenerateSchemaJsonResult:
        json_schema = Blueprint.model_json_schema()
        content = json.dumps(
            json_schema,
            indent=2,
            sort_keys=True,
            separators=(",", ":"),
        )
        self.file_system_port.write_file(
            path=Path("codegen.schema.json"),
            content=content,
            overwrite=True,
        )
        return GenerateSchemaJsonResult()
