from pathlib import Path

from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.services.dependency_resolver import DependencyResolver
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.ports.template_port import TemplatePort
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratePackageCommand:
    """Command/Query for GeneratePackage."""

    package_spec: PackageSpec
    overwrite: bool
    node: str | None = None


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
        dependency_resolver = DependencyResolver.build_from_package_spec(
            cmd.package_spec
        )
        self._execute_recursive(
            root_path=None,
            package_spec=cmd.package_spec,
            overwrite=cmd.overwrite,
            dependency_resolver=dependency_resolver,
        )
        return GeneratePackageResult(result="success")

    def _execute_recursive(
        self,
        root_path: Path | None,
        package_spec: PackageSpec,
        dependency_resolver: DependencyResolver,
        overwrite: bool = False,
        node: str | None = None,
    ):
        if root_path:
            current_path = root_path / package_spec.name
        else:
            current_path = Path(package_spec.name)
        for module in package_spec.modules:
            if node and node != module.name and not module.is_init_module():
                continue
            imports = dependency_resolver.resolve_module(
                module_spec=module,
            )
            context = {"module_spec": module, "imports": imports}
            content = self.template_port.render("module.j2", context)
            module_path = current_path / module.filename
            self.file_system_port.write_file(
                path=module_path,
                content=content,
                overwrite=overwrite,
            )
        for subpackage in package_spec.sub_packages:
            if node and node == subpackage.name:
                node = None
            self._execute_recursive(
                root_path=current_path,
                package_spec=subpackage,
                dependency_resolver=dependency_resolver,
                overwrite=overwrite,
                node=node,
            )
