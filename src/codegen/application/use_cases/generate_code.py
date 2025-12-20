from dataclasses import dataclass

from codegen.domain.ports.blueprint_loader_port import BlueprintLoaderPort
from codegen.domain.ports.file_system_port import FileSystemPort
from codegen.domain.ports.template_port import TemplatePort
from codegen.domain.services.naming_service import NamingService
from codegen.domain.services.scaffold_service import ScaffoldService
from codegen.domain.services.template_context_builder import TemplateContextBuilder


@dataclass(frozen=True)
class GenerateCodeCommand:
    """Command/Query for GenerateCode."""

    overwrite: bool  #
    node: str  #


@dataclass(frozen=True)
class GenerateCodeResult:
    """Result of GenerateCode."""

    files_written: list[str]  #


@dataclass
class GenerateCodeHandler:
    """Handler for GenerateCode (command)."""

    naming_service: NamingService
    scaffold_service: ScaffoldService
    template_context_builder: TemplateContextBuilder
    template_port: TemplatePort
    file_system_port: FileSystemPort
    blueprint_loader: BlueprintLoaderPort

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:

        blueprint = self.blueprint_loader.load("codegen.yaml")
        if blueprint is None:
            return GenerateCodeResult(files_written=[])

        self.template_context_builder.build_registry(blueprint)

        render_tasks = self.scaffold_service.plan_generation(
            blueprint,
            template_context_builder=self.template_context_builder,
        )
        written_files: list[str] = []

        for task in render_tasks:
            content = self.template_port.render(task.template_name, task.context_data)
            self.file_system_port.write_text(task.target_path, content)
            written_files.append(task.target_path)

        return GenerateCodeResult(files_written=written_files)
