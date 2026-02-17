import time
from pathlib import Path
from codegen.orchestration.domain.enums import BuildStatus, FileStatus
from codegen.orchestration.domain.value_objects.file_result import FileResult
from codegen.orchestration.domain.value_objects.build_result import BuildResult
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

    result: BuildResult


@dataclass
class GeneratePackage:

    file_system_port: FileSystemPort
    translator: PythonSyntaxTranslator
    code_formatter: CodeFormatter

    def execute(self, cmd: GeneratePackageCommand) -> GeneratePackageResult:
        start_time = time.time()
        build_result = BuildResult(status=BuildStatus.SUCCESS)

        try:
            current_pkg_path = Path(cmd.package_spec.name)
            if self.file_system_port.is_directory(current_pkg_path):
                current_pkg = self.translator.to_package_spec(
                    package_path=Path(cmd.package_spec.name)
                )
                pkg = cmd.package_spec.merge(current_pkg)
            else:
                pkg = cmd.package_spec
            
            source_tree = self.translator.generate_source_tree(
                package_spec=pkg, target_node=cmd.node, root_path=cmd.root_path
            )

            for rel_path_str, content in source_tree.items():
                rel_path = Path(rel_path_str)
                try:
                    # Formatting
                    try:
                        content = self.code_formatter.format_code(content)
                    except Exception as fe:
                        logger.warning(f"Failed to format code for {rel_path}: {fe}")
                        # We still try to write it, but we could mark it. 
                        # For now, let's just use the unformatted content.

                    # Check existence and content
                    if not self.file_system_port.exists(rel_path):
                        status = FileStatus.CREATED
                    else:
                        if cmd.overwrite:
                            status = FileStatus.UPDATED
                        else:
                            status = FileStatus.SKIPPED

                    if status != FileStatus.SKIPPED:
                        self.file_system_port.write_file(
                            path=rel_path, content=content, overwrite=cmd.overwrite
                        )
                    
                    build_result.add_file_result(FileResult(path=str(rel_path), status=status))

                except Exception as e:
                    logger.error(f"Failed to generate {rel_path}: {e}")
                    build_result.add_file_result(FileResult(
                        path=str(rel_path), 
                        status=FileStatus.FAILED, 
                        message=str(e)
                    ))

        except Exception as e:
            logger.critical(f"Critical error during package generation: {e}")
            build_result.status = BuildStatus.FAILURE
            build_result.messages.append(str(e))
        
        finally:
            build_result.stats.duration_ms = int((time.time() - start_time) * 1000)

        return GeneratePackageResult(result=build_result)
