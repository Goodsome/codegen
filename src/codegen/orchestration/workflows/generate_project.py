from codegen.orchestration.translators.blueprint_to_package_spec import (
    BlueprintToPackageSpecTranslator,
)
from dataclasses import dataclass

from codegen.application.use_cases.load_blueprint import (
    LoadBlueprintHandler,
    LoadBlueprintCommand,
)
from codegen.python_gen.application.use_cases.generate_module import (
    GenerateModuleHandler,
    GenerateModuleCommand,
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
class GenerateCodeWorkflow:
    loader: LoadBlueprintHandler
    translator: BlueprintToPackageSpecTranslator
    generator: GenerateModuleHandler

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:
        """Orchestrates blueprint loading and module generation"""
        load_result = self.loader.execute(LoadBlueprintCommand(node=cmd.node))
        if load_result.blueprint is None:
            return GenerateCodeResult(files_written=[])

        package_spec = self.translator.execute(load_result.blueprint)

        for module in package_spec.modules:
            generate_module_cmd = GenerateModuleCommand(
                module_spec=module,
                overwrite=cmd.overwrite,
            )
            self.generator.execute(generate_module_cmd)

        return GenerateCodeResult(files_written=[])
