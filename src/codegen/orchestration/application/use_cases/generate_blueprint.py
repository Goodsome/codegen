from dataclasses import dataclass
from codegen.python_gen.application.use_cases.parse_package import (
    ParsePackage,
    ParsePackageQuery,
)
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from typing import Self
from codegen.orchestration.application.dtos.generate_blueprint_result import (
    GenerateBlueprintResult,
)
from codegen.orchestration.application.dtos.generate_blueprint_command import (
    GenerateBlueprintCommand,
)


@dataclass
class GenerateBlueprint:
    parser: ParsePackage
    storage: BlueprintStorage

    def execute(self: Self, cmd: GenerateBlueprintCommand) -> GenerateBlueprintResult:
        project_pkg = self.parser.execute(
            ParsePackageQuery(package_path=cmd.path)
        ).package_spec
        test_pkg = self.parser.execute(
            ParsePackageQuery(package_path=cmd.test_path)
        ).package_spec
        blueprint = Blueprint.from_package_spec(project_pkg)
        blueprint.load_test_package(test_pkg)
        self.storage.save(blueprint)
        return GenerateBlueprintResult(result="Generated blueprint.")
