from codegen.python_gen.domain.aggregates.package_spec import PackageSpec
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.ports.template_port import TemplatePort
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratePackageCommand:
    """Command/Query for GeneratePackage."""

    package_spec: PackageSpec  #
    overwrite: bool  #


@dataclass(frozen=True)
class GeneratePackageResult:
    """Result of GeneratePackage."""

    result: str  #


@dataclass
class GeneratePackageHandler:
    """Generate Python package."""

    template_port: TemplatePort
    file_system_port: FileSystemPort

    def execute(self, cmd: GeneratePackageCommand) -> GeneratePackageResult:
        for module in cmd.package_spec.modules:
            context = {"module_spec": module}
            content = self.template_port.render("module.j2", context)
            self.file_system_port.write_file(
                path=module.full_path,
                content=content,
                overwrite=cmd.overwrite,
            )
        return GeneratePackageResult(result="success")
