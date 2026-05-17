import ast
import difflib
from dataclasses import dataclass
from pathlib import Path

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from codegen.code_metadata.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class DevProgressService:
    file_system_port: FileSystemPort
    generator: CodeGenerator

    def get_dev_progress(
        self,
        context: str,
        components: dict[str, Component],
        dep_components: dict[ComponentId, ComponentDTO],
    ) -> DevProgress:
        context_path = Path("src/codegen") / context
        current_files = self.file_system_port.list_directory_recursively(
            path=context_path, pattern="*.py"
        )
        file_metrics: list[FileMetrics] = []
        for file_path in current_files:
            file_name = file_path.stem
            if file_name == "__init__":
                continue
            component = components.get(file_name)
            if component and component.context != context:
                continue
            file_metrics.append(
                self.get_file_metrics(
                    file_path,
                    component,
                    dep_components=dep_components,
                )
            )

        return DevProgress(records=file_metrics)

    def get_file_metrics(
        self,
        file_path: Path,
        component: Component | None,
        dep_components: dict[ComponentId, ComponentDTO],
    ) -> FileMetrics:
        file_name = file_path.stem
        origin_code = self.file_system_port.read_file(file_path)
        original_lines = len(origin_code.splitlines())
        if component:
            component_type = str(component.type)
            component_code = self.generator.generate(
                component=component, dep_components=dep_components
            )
            generated_lines = len(component_code.splitlines())
            ast_similarity = self.calculate_ast_similarity(origin_code, component_code)
        else:
            component_code = ""
            component_type = "unknown"
            ast_similarity = 0
            generated_lines = 0
        return FileMetrics(
            file_name=file_name,
            component_type=component_type,
            ast_similarity=ast_similarity,
            original_lines=original_lines,
            generated_lines=generated_lines,
            original_code=origin_code,
            generated_code=component_code,
        )

    def calculate_ast_similarity(
        self, original_code: str, generated_code: str
    ) -> float:
        tree_orig = ast.parse(original_code)
        tree_gen = ast.parse(generated_code)

        dump_orig = ast.dump(tree_orig, annotate_fields=True, include_attributes=False)
        dump_gen = ast.dump(tree_gen, annotate_fields=True, include_attributes=False)

        matcher = difflib.SequenceMatcher(
            None,
            dump_orig.replace("(", "\n").splitlines(),
            dump_gen.replace("(", "\n").splitlines(),
        )
        return matcher.ratio()
