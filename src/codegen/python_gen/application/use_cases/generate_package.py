from dataclasses import dataclass

from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.ports.template_port import TemplatePort


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
        from codegen.python_gen.domain.services.python_syntax_translator import (
            PythonSyntaxTranslator,
        )

        translator = PythonSyntaxTranslator(template_port=self.template_port)
        source_tree = translator.generate_source_tree(
            package_spec=cmd.package_spec,
            target_node=cmd.node,
        )
        for rel_path, content in source_tree.items():
            self.file_system_port.write_file(
                path=rel_path,
                content=content,
                overwrite=cmd.overwrite,
            )
        return GeneratePackageResult(result=f"Generated {len(source_tree)} files.")
