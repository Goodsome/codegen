from codegen.python_gen.application.translators.blueprint_trans import (
    BlueprintTranslator,
)
from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackage,
    GeneratePackageCommand,
)
from dataclasses import dataclass, field

from codegen.domain_definition.application.use_cases.load_blueprint import (
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
    generator: GeneratePackage
    translator: BlueprintTranslator

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:
        """Orchestrates blueprint loading and module generation"""
        load_result = self.loader.execute(LoadBlueprintCommand(node=cmd.node))
        if load_result.blueprint is None:
            return GenerateCodeResult(files_written=[])

        package_spec = self.translator.translate_blueprint(load_result.blueprint)
        self.generator.execute(
            GeneratePackageCommand(
                package_spec=package_spec,
                overwrite=cmd.overwrite,
                node=cmd.node,
            )
        )

        return GenerateCodeResult(files_written=[])
