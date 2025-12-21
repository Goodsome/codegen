from dataclasses import dataclass

from codegen.domain.ports.blueprint_loader_port import BlueprintLoaderPort
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.ports.template_port import TemplatePort
from codegen.domain.services.scaffold_service import ScaffoldService


@dataclass(frozen=True)
class GenerateCodeCommand:
    """Command/Query for GenerateCode."""

    overwrite: bool
    node: str | None = None
    target_path: str = "target"


@dataclass(frozen=True)
class GenerateCodeResult:
    """Result of GenerateCode."""

    files_written: list[str]  #


@dataclass
class GenerateCodeHandler:
    """Handler for GenerateCode (command)."""

    scaffold_service: ScaffoldService
    template_port: TemplatePort
    file_system_port: FileSystemPort
    blueprint_loader: BlueprintLoaderPort

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:

        blueprint = self.blueprint_loader.load("codegen.yaml")
        if blueprint is None:
            return GenerateCodeResult(files_written=[])

        render_tasks = self.scaffold_service.plan_generation(
            blueprint,
            node=cmd.node,
        )
        written_files: list[str] = []

        for task in render_tasks:
            content = self.template_port.render(task.template_name, task.context_data)
            target_path = f"{cmd.target_path}/{task.target_path}"
            print(f"Writing {target_path}, {cmd.overwrite}")
            self.file_system_port.write_file(
                path=target_path,
                content=content,
                overwrite=cmd.overwrite,
            )
            written_files.append(task.target_path)

        return GenerateCodeResult(files_written=written_files)
