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
from typing import Union
from pydantic import BaseModel, Field


class GenerateProjectCommand(BaseModel):
    nodes: list[str] | None = Field(default=None)
    root_path: str = Field(default="")
    generate_tests: bool = Field(default=False)


class GenerateProjectResult(BaseModel):
    result: BuildResult


@dataclass
class GenerateProject:
    loader: LoadBlueprint
    generator: GeneratePackage

    def execute(self, cmd: GenerateProjectCommand) -> GenerateProjectResult:
        node = cmd.nodes[0] if cmd.nodes and len(cmd.nodes) == 1 else None
        load_result = self.loader.execute(LoadBlueprintCommand(node=node))
        package_spec = load_result.blueprint.to_package_spec()
        gen_result = self.generator.execute(
            GeneratePackageCommand(
                package_spec=package_spec,
                nodes=cmd.nodes,
                overwrite=cmd.nodes is not None,
                root_path=cmd.root_path,
            )
        )
        return GenerateProjectResult(result=gen_result.result)
