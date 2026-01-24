from dataclasses import dataclass, field
from codegen.orchestration.domain.services.blueprint_mapper import BlueprintMapper
from codegen.python_gen.application.use_cases.parse_package import (
    ParsePackage,
    ParsePackageQuery,
)
from pathlib import Path
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


@dataclass(frozen=True)
class GenerateBlueprintCommand:

    path: Path


@dataclass(frozen=True)
class GenerateBlueprintResult:

    result: str


@dataclass
class GenerateBlueprint:

    parser: ParsePackage
    storage: BlueprintStorage
    mapper: BlueprintMapper = field(default_factory=BlueprintMapper)

    def execute(self, cmd: GenerateBlueprintCommand) -> GenerateBlueprintResult:
        project_pkg = self.parser.execute(
            ParsePackageQuery(package_path=cmd.path)
        ).package_spec
        blueprint = self.mapper.to_blueprint(project_pkg)
        self.storage.save(blueprint)
        return GenerateBlueprintResult(result="Generated blueprint.")
