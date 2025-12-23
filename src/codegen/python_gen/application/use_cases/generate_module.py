from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.ports.template_port import TemplatePort
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateModuleCommand:
    """Command/Query for GenerateModule."""

    module_spec: ModuleSpec  #
    overwrite: bool  #


@dataclass(frozen=True)
class GenerateModuleResult:
    """Result of GenerateModule."""

    result: str  #


@dataclass
class GenerateModuleHandler:
    """Generate Python module."""

    template_port: TemplatePort
    file_system_port: FileSystemPort

    def execute(self, cmd: GenerateModuleCommand) -> GenerateModuleResult:
        context = {"module_spec": cmd.module_spec}
        content = self.template_port.render("module.j2", context)
        self.file_system_port.write_file(
            path=cmd.module_spec.full_path,
            content=content,
            overwrite=cmd.overwrite,
        )
        return GenerateModuleResult(result="success")
