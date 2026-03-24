from dataclasses import dataclass
from codegen.orchestration.domain.value_objects.build_result import BuildResult
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)
from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackage,
    GeneratePackageCommand,
)


@dataclass(frozen=True)
class GenerateProjectCommand:

    overwrite: bool
    nodes: list[str] | None
    root_path: str = ""
    generate_tests: bool = False


@dataclass(frozen=True)
class GenerateProjectResult:

    result: BuildResult


@dataclass
class GenerateProject:

    loader: LoadBlueprint
    generator: GeneratePackage

    def execute(self, cmd: GenerateProjectCommand) -> GenerateProjectResult:

        # For backward compatibility, pass first node as `node` for single-node scenarios
        node = cmd.nodes[0] if cmd.nodes and len(cmd.nodes) == 1 else None

        load_result = self.loader.execute(LoadBlueprintCommand(node=node))
        package_spec = load_result.blueprint.to_package_spec()
        gen_result = self.generator.execute(
            GeneratePackageCommand(
                package_spec=package_spec,
                nodes=cmd.nodes,
                overwrite=cmd.overwrite,
                root_path=cmd.root_path,
            )
        )
        return GenerateProjectResult(result=gen_result.result)
