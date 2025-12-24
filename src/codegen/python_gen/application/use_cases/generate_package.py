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
class GeneratePackage:
    """Generate Python package."""

    template_port: TemplatePort
    file_system_port: FileSystemPort

    def execute(self, cmd: GeneratePackageCommand) -> GeneratePackageResult:
        package_spec = cmd.package_spec
        if not package_spec.has_init_file():
            self.file_system_port.write_file(
                path=package_spec.path / "__init__.py",
                content="",
            )
        for module in cmd.package_spec.modules:
            context = {"module_spec": module}
            content = self.template_port.render("module.j2", context)
            self.file_system_port.write_file(
                path=module.full_path,
                content=content,
                overwrite=cmd.overwrite,
            )
        for subpackage in cmd.package_spec.packages:
            _cmd = GeneratePackageCommand(
                package_spec=subpackage, overwrite=cmd.overwrite
            )
            self.execute(_cmd)
        return GeneratePackageResult(result="success")
