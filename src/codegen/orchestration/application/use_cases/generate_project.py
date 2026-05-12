from dataclasses import dataclass
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)
from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackage,
    GeneratePackageCommand,
)
from codegen.orchestration.application.dtos.generate_project_result import (
    GenerateProjectResult,
)
from typing import Self
from codegen.orchestration.application.dtos.generate_project_command import (
    GenerateProjectCommand,
)


@dataclass
class GenerateProject:
    loader: LoadBlueprint
    generator: GeneratePackage

    def execute(self: Self, cmd: GenerateProjectCommand) -> GenerateProjectResult:
        node = cmd.nodes[0] if cmd.nodes and len(cmd.nodes) == 1 else None
        load_result = self.loader.execute(LoadBlueprintCommand(node=node))
        package_spec = load_result.blueprint.to_package_spec()
        tps = load_result.blueprint.to_test_package_spec()
        overwrite = False
        if cmd.nodes:
            overwrite = True
        gen_result = self.generator.execute(
            GeneratePackageCommand(
                package_spec=package_spec, nodes=cmd.nodes, overwrite=overwrite
            )
        )
        gen_tests_result = self.generator.execute(
            GeneratePackageCommand(package_spec=tps)
        )
        return GenerateProjectResult(
            result=gen_result.result, tests_result=gen_tests_result.result
        )
