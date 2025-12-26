from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackage,
    GeneratePackageCommand,
)
from codegen.orchestration.translators.blueprint_to_package_spec import (
    BlueprintToPackageSpecTranslator,
)
from dataclasses import dataclass

from codegen.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)


@dataclass(frozen=True)
class GenerateCodeCommand:
    """Command/Query for GenerateCode."""

    overwrite: bool = False
    node: str | None = None


@dataclass(frozen=True)
class GenerateCodeResult:
    """Result of GenerateCode."""

    files_written: list[str]


@dataclass
class GenerateProject:
    loader: LoadBlueprint
    translator: BlueprintToPackageSpecTranslator
    generator: GeneratePackage

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:
        """Orchestrates blueprint loading and module generation"""
        load_result = self.loader.execute(LoadBlueprintCommand(node=cmd.node))
        if load_result.blueprint is None:
            return GenerateCodeResult(files_written=[])

        package_spec = self.translator.execute(load_result.blueprint)
        self.generator.execute(
            GeneratePackageCommand(
                package_spec=package_spec,
                overwrite=cmd.overwrite,
                node=cmd.node,
            )
        )

        return GenerateCodeResult(files_written=[])
