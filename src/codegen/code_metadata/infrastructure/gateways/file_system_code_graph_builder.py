from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import override

from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
    GetProjectDocumentsQuery,
)
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.dtos.code_node_dto import (
    ClassNodeDto,
    CodeNodeDto,
    DirectoryNodeDto,
    ExternalNodeDto,
    FileNodeDto,
    FunctionNodeDto,
    MethodNodeDto,
    ModuleNodeDto,
    VariableNodeDto,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt


@dataclass
class FileSystemCodeGraphBuilder(CodeGraphBuilder):
    """从文件系统构建 CodeNode 图的实现。

    通过 GetProjectDocumentsHandler 获取项目文档列表，
    再从文档路径派生目录树结构，同步完成节点构造和 CONTAINS 边的建立。
    """

    get_project_documents: GetProjectDocumentsHandler

    @override
    def build(self, fqn_prefix: str) -> list[CodeNodeDto]:
        context_path = Path(fqn_prefix)

        query = GetProjectDocumentsQuery(dir_path=context_path)
        result = self.get_project_documents.handle(query)

        acl = CodeGraphAcl(root_path=context_path)
        nodes = acl.build_nodes(result.code_documents)

        return nodes


@dataclass
class CodeGraphAcl:
    root_path: Path
    nodes: list[CodeNodeDto] = field(default_factory=list)
    node_register: dict[str, CodeNodeDto] = field(default_factory=dict)
    overload_index: dict[str, int] = field(default_factory=dict)
    collect_imports: defaultdict[str, list[AstImport | AstImportFrom]] = field(
        default_factory=lambda: defaultdict(list)
    )
    local_aliases: dict[str, str] = field(default_factory=dict)

    def build_nodes(self, code_documents: list[CodeDocument]) -> list[CodeNodeDto]:
        self._build_directory_nodes(code_documents)
        self._build_file_nodes(code_documents)
        self._build_imports_edges()

        return list(self.node_register.values())

    def _add_node(self, dto: CodeNodeDto) -> None:
        if dto.fqn in self.node_register:
            raise ValueError(f"Duplicate: {dto.fqn=}")
        self.node_register[dto.fqn] = dto

    def _get_ovrload_index(self, fqn: str) -> int:
        if fqn not in self.overload_index:
            self.overload_index[fqn] = 0
        self.overload_index[fqn] += 1
        return self.overload_index[fqn] - 1

    def _build_directory_nodes(self, code_documents: list[CodeDocument]) -> None:
        dir_paths: set[Path] = set()
        for doc in code_documents:
            parent = doc.physical_path.parent
            while parent != self.root_path and self.root_path in parent.parents:
                dir_paths.add(parent)
                parent = parent.parent

        for dir_path in sorted(dir_paths, key=lambda p: len(p.parts)):
            self._build_directory_node(dir_path)

    def _build_file_nodes(self, code_documents: list[CodeDocument]) -> None:
        for doc in code_documents:
            self._build_file_node(doc)

    def _build_directory_node(self, path: Path) -> DirectoryNodeDto:
        fqn = self._dir_fqn(path)
        dto = DirectoryNodeDto(fqn=fqn, name=path.name or fqn)
        # 为父目录添加 CONTAINS 边
        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in self.node_register:
            parent_node = self.node_register[parent_fqn]
            assert isinstance(parent_node, DirectoryNodeDto)
            parent_node.contains(dto)

        self._add_node(dto)

        return dto

    def _build_file_node(self, code_document: CodeDocument) -> None:
        path = code_document.physical_path
        fqn = self._file_fqn(path)
        file_dto = FileNodeDto(fqn=fqn, name=path.name)

        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in self.node_register:
            parent_node = self.node_register[parent_fqn]
            assert isinstance(parent_node, DirectoryNodeDto)
            parent_node.contains(file_dto)

        self._add_node(file_dto)
        self._build_module_node(code_document, file_dto)

    def _build_module_node(
        self, code_document: CodeDocument, file_node: FileNodeDto
    ) -> ModuleNodeDto:
        path = code_document.physical_path
        module_fqn = self._module_fqn(path)
        module_node = ModuleNodeDto(
            fqn=module_fqn, name=module_fqn.rsplit(".", maxsplit=1)[-1]
        )
        self._add_node(module_node)
        file_node.defines_module(module_node)

        for stmt in code_document.body:
            self._parse_stmt(stmt, module_node)

            if isinstance(stmt, AstImport | AstImportFrom):
                self.collect_imports[module_fqn].append(stmt)

        return module_node

    def _parse_stmt(
        self, stmt: AstStmt, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        match stmt:
            case AstClassDef():
                assert isinstance(parent_node, ModuleNodeDto)
                self._parse_class_def(stmt, parent_node)
            case AstFunctionDef():
                self._parse_function_def(stmt, parent_node)
            case AstAnnAssign():
                self._parse_ann_assign(stmt, parent_node)
            case AstAssign():
                self._parse_assign(stmt, parent_node)
            case _:
                pass

    def _parse_class_def(
        self, class_def: AstClassDef, module_node: ModuleNodeDto
    ) -> ClassNodeDto:
        class_fqn = f"{module_node.fqn}::{class_def.name}"
        dto = ClassNodeDto(fqn=class_fqn, name=class_def.name)
        module_node.contains(dto)
        for stmt in class_def.body:
            self._parse_stmt(stmt, dto)

        self._add_node(dto)
        return dto

    def _parse_function_def(
        self, func_def: AstFunctionDef, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> FunctionNodeDto | MethodNodeDto:
        func_fqn = f"{parent_node.fqn}::{func_def.name}"
        if func_def.is_overload:
            overload_index = self._get_ovrload_index(func_fqn)
            func_fqn = f"{func_fqn}::<overload_{overload_index}>"
        match parent_node:
            case ClassNodeDto():
                dto = MethodNodeDto(fqn=func_fqn, name=func_def.name)
                parent_node.contains(dto)
            case ModuleNodeDto():
                dto = FunctionNodeDto(fqn=func_fqn, name=func_def.name)
                parent_node.contains(dto)
        self._add_node(dto)
        return dto

    def _parse_ann_assign(
        self, ann_assign: AstAnnAssign, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        target = ann_assign.target
        if not isinstance(target, AstName):
            return
        var_fqn = f"{parent_node.fqn}::{target.id}"
        dto = VariableNodeDto(fqn=var_fqn, name=target.id)
        parent_node.contains(dto)
        self._add_node(dto)

    def _parse_assign(
        self, assign: AstAssign, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        if not assign.targets:
            return
        if not len(assign.targets) == 1:
            return
        target = assign.targets[0]
        if not isinstance(target, AstName):
            return
        var_fqn = f"{parent_node.fqn}::{target.id}"
        dto = VariableNodeDto(fqn=var_fqn, name=target.id)
        parent_node.contains(dto)
        self._add_node(dto)

    def _build_imports_edges(self) -> None:
        for fqn, imports in self.collect_imports.items():
            module_node = self.node_register[fqn]
            assert isinstance(module_node, ModuleNodeDto)
            for import_ in imports:
                match import_:
                    case AstImport():
                        self._parse_import(import_, module_node)
                    case _:
                        pass

    def _parse_import(self, import_: AstImport, module_node: ModuleNodeDto) -> None:
        for name in import_.names:
            self._parse_import_name(name.name, module_node, asname=name.asname)

    def _parse_import_from(
        self, import_from: AstImportFrom, module_node: ModuleNodeDto
    ) -> None:
        if import_from.level > 0:
            module_prefix = module_node.get_parent_by_level(import_from.level)
        else:
            module_prefix = ""

        module = module_prefix + (import_from.module or "")
        if not module:
            raise ValueError(f"ImportFrom module is empty: {import_from.module}")

        for name in import_from.names:
            self._parse_import_name(
                name.name,
                module_node,
                from_name=module,
                asname=name.asname,
            )

    def _parse_import_name(
        self,
        import_name: str,
        module_node: ModuleNodeDto,
        from_name: str | None = None,
        asname: str | None = None,
    ) -> None:
        if from_name:
            is_external = not from_name.startswith("codegen.")
        else:
            is_external = not import_name.startswith("codegen.")

        if is_external:
            external_fqn = f"{from_name}.{import_name}" if from_name else import_name
            node = self._ensure_external_node(external_fqn)
        else:
            node = self._get_internel_node(
                import_name=import_name,
                from_name=from_name,
            )
        assert isinstance(
            node, ExternalNodeDto | ClassNodeDto | FunctionNodeDto | VariableNodeDto
        )
        module_node.imports(node)
        if asname:
            local_alias_key = f"{module_node.fqn}|{asname}"
        else:
            local_alias_key = f"{module_node.fqn}|{node.name}"
            
        self.local_aliases[local_alias_key] = node.fqn

    def _ensure_external_node(self, fqn: str) -> CodeNodeDto:
        if fqn in self.node_register:
            return self.node_register[fqn]
        return self._build_external_node(fqn)

    def _get_internel_node(
        self,
        import_name: str,
        from_name: str | None,
    ) -> CodeNodeDto:
        name = import_name
        if from_name is None:
            return self.node_register[name]
        module_fqn = f"{from_name}.{name}"
        if module_fqn in self.node_register:
            return self.node_register[module_fqn]
        other_fqn = f"{from_name}::{name}"
        if other_fqn in self.node_register:
            return self.node_register[other_fqn]
        raise ValueError(f"Cannot resolve import: {import_name} from {from_name}")
        

    def _build_external_node(self, fqn: str) -> ExternalNodeDto:
        node = ExternalNodeDto(
            name=fqn.split(".", maxsplit=1)[-1],
            fqn=fqn,
        )
        self._add_node(node)
        return node

    def _dir_fqn(self, path: Path) -> str:
        """目录 FQN：相对路径/，以 / 结尾。根目录为 /。"""
        if path == Path("."):
            return "/"
        return f"{path.as_posix()}/"

    def _file_fqn(self, path: Path) -> str:
        """文件 FQN：相对文件路径。"""
        return path.as_posix()

    def _module_fqn(self, path: Path) -> str:
        """模块 FQN：将路径分隔符替换为 '.'，去除后缀。

        __init__.py 映射到其所在目录的包名(如 src/foo/__init__.py → src.foo),
        其余文件映射到模块路径(如 src/foo/bar.py → src.foo.bar)。
        """
        if path.name == "__init__.py":
            return ".".join(path.parent.parts)
        return ".".join(path.with_suffix("").parts)
