from pathlib import Path
from codegen.python_gen.domain.ports.code_formatter import CodeFormatter
from dataclasses import dataclass, field
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.services.python_syntax_translator import (
    PythonSyntaxTranslator,
)
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from logging import getLogger

logger = getLogger(__name__)


@dataclass(frozen=True)
class GeneratePackageCommand:

    package_spec: PackageSpec
    overwrite: bool
    node: str | None = field(default=None)
    root_path: str = field(default="")


@dataclass(frozen=True)
class GeneratePackageResult:

    result: str


@dataclass
class GeneratePackage:

    file_system_port: FileSystemPort
    translator: PythonSyntaxTranslator
    code_formatter: CodeFormatter

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
            package_spec=pkg, target_node=cmd.node,
            root_path=cmd.root_path,
        )
        for rel_path, content in source_tree.items():
            try:
                content = self.code_formatter.format_code(content)
            except Exception as e:
                logger.warning(f"Failed to format code for {rel_path}: {e}")

            self.file_system_port.write_file(
                path=rel_path, content=content, overwrite=cmd.overwrite
            )
        return GeneratePackageResult(result=f"Generated {len(source_tree)} files.")
