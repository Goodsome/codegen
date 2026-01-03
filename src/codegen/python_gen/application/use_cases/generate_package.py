from dataclasses import dataclass
from pathlib import Path

from codegen.python_gen.domain.services.python_syntax_translator import (
    PythonSyntaxTranslator,
)
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass(frozen=True)
class GeneratePackageCommand:
    """Command/Query for GeneratePackage."""

    package_spec: PackageSpec
    overwrite: bool
    node: str | None = None


@dataclass(frozen=True)
class GeneratePackageResult:
    """Result of GeneratePackage."""

    result: str


@dataclass
class GeneratePackage:
    """Generate Python package."""

    file_system_port: FileSystemPort
    translator: PythonSyntaxTranslator

    def execute(self, cmd: GeneratePackageCommand) -> GeneratePackageResult:
        current_pkg_path = Path(cmd.package_spec.name)
        if self.file_system_port.is_directory(current_pkg_path):
            current_pkg = self.translator.to_package_spec(
                package_path=Path(cmd.package_spec.name)
            )
            pkg = cmd.package_spec.merge(current_pkg)
        else:
            pkg = cmd.package_spec
        source_tree = self.translator.generate_source_tree(
            package_spec=pkg,
            target_node=cmd.node,
        )
        for rel_path, content in source_tree.items():
            self.file_system_port.write_file(
                path=rel_path,
                content=content,
                overwrite=cmd.overwrite,
            )
        return GeneratePackageResult(result=f"Generated {len(source_tree)} files.")
