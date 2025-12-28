from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from codegen.python_gen.domain.services.dependency_resolver import DependencyResolver
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.ports.template_port import TemplatePort


@dataclass
class PythonSyntaxTranslator:
    """Bidirectional translator between Python source code and PackageSpec."""

    template_port: TemplatePort
    file_system_port: FileSystemPort

    def to_package_spec(self, package_path: Path) -> PackageSpec:
        """
        Reconstruct a PackageSpec from a dictionary of file paths and their contents.
        """

        if not self.file_system_port.is_directory(package_path):
            raise ValueError(f"Expected a directory, got {package_path}")
        package_name = package_path.stem
        modules: list[ModuleSpec] = []
        sub_packages: list[PackageSpec] = []
        for filepath in self.file_system_port.list_directory_flat(package_path):
            if self.file_system_port.is_file(filepath) and filepath.suffix == ".py":
                source_code = self.file_system_port.read_file(filepath)
                modules.append(ModuleSpec.parse_code(source_code, filepath.stem))
            elif self.file_system_port.is_directory(filepath):
                sub_packages.append(self.to_package_spec(filepath))

        return PackageSpec.create(
            name=package_name,
            modules=modules,
            sub_packages=sub_packages,
        )

    def to_code(
        self, module_spec: ModuleSpec, imports: Iterable[ImportFromSpec]
    ) -> str:
        context = {"module_spec": module_spec, "imports": imports}
        content = self.template_port.render("module.j2", context)
        return content

    def generate_source_tree(
        self, package_spec: PackageSpec, target_node: str | None
    ) -> dict[Path, str]:
        """
        核心方法：将 PackageSpec 转换为虚拟文件树。
        返回格式: { Path('relative/path/to/file.py'): 'source code content' }
        """
        # 1. 预先构建依赖解析器
        resolver = DependencyResolver.build_from_package_spec(package_spec)

        # 2. 结果容器
        virtual_files: dict[Path, str] = {}

        # 3. 递归生成
        self._collect_files_recursively(
            current_spec=package_spec,
            resolver=resolver,
            output_dict=virtual_files,
            current_path=Path(package_spec.name),  # 根目录名
            target_node=target_node,
        )

        return virtual_files

    def _collect_files_recursively(
        self,
        current_spec: PackageSpec,
        resolver: DependencyResolver,
        output_dict: dict[Path, str],
        current_path: Path,
        target_node: str | None,
    ) -> None:
        # 处理当前包下的 Modules
        for module in current_spec.modules:
            # 过滤逻辑下沉到这里
            if (
                target_node
                and target_node != module.name
                and not module.is_init_module()
            ):
                continue

            # 解析导入依赖
            imports = resolver.resolve_module(module)

            # 生成代码 (调用单文件生成逻辑)
            source_code = self.to_code(module, imports)

            # 记录文件路径和内容
            file_path = current_path / module.filename
            output_dict[file_path] = source_code

        # 处理子包 (递归)
        for subpackage in current_spec.sub_packages:
            self._collect_files_recursively(
                current_spec=subpackage,
                resolver=resolver,
                output_dict=output_dict,
                current_path=current_path / subpackage.name,
                target_node=target_node,
            )
