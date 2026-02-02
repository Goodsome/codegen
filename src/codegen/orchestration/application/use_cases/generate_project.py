from dataclasses import dataclass, field

from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)
from codegen.orchestration.domain.services.blueprint_mapper import BlueprintMapper
from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackage,
    GeneratePackageCommand,
)


@dataclass(frozen=True)
class GenerateProjectCommand:

    overwrite: bool
    node: str | None
    root_path: str = ""


@dataclass(frozen=True)
class GenerateProjectResult:

    result: str


@dataclass
class GenerateProject:

    loader: LoadBlueprint
    generator: GeneratePackage
    mapper: BlueprintMapper = field(default_factory=BlueprintMapper)

    def execute(self, cmd: GenerateProjectCommand) -> GenerateProjectResult:
        load_result = self.loader.execute(LoadBlueprintCommand(node=cmd.node))
        package_spec = self.mapper.to_package_spec(load_result.blueprint)
        self.generator.execute(
            GeneratePackageCommand(
                package_spec=package_spec,
                node=cmd.node,
                overwrite=cmd.overwrite,
                root_path=cmd.root_path,
            )
        )
        return GenerateProjectResult(
            result=f"Generated {len(package_spec.sub_packages)} packages."
        )
