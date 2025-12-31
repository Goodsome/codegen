from dataclasses import dataclass, field
from codegen.orchestration.domain.services.blueprint_mapper import BlueprintMapper
from codegen.python_gen.application.use_cases.parse_package import (
    ParsePackage,
    ParsePackageQuery,
)
from pathlib import Path
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


@dataclass(frozen=True)
class UpdateBlueprintCommand:

    path: Path


@dataclass(frozen=True)
class UpdateBlueprintResult:

    result: str


@dataclass
class UpdateBlueprint:

    parser: ParsePackage
    storage: BlueprintStorage
    mapper: BlueprintMapper = field(default_factory=BlueprintMapper)

    def execute(self, cmd: UpdateBlueprintCommand) -> UpdateBlueprintResult:
        project_pkg = self.parser.execute(
            ParsePackageQuery(package_path=cmd.path)
        ).package_spec
        blueprint = self.mapper.to_blueprint(project_pkg)
        self.storage.save(blueprint, "target/codegen.yaml")
        return UpdateBlueprintResult(result="Updated blueprint.")
