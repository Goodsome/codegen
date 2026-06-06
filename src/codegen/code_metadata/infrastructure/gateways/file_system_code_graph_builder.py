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
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.domain.value_objects import AstExpr, AstIf, AstSubscript
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.shared.domain.enums import PythonBuiltinType


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

        node_registry = NodeRegistry()

        acl = CodeGraphAcl(
            fqn_factory=FqnFactory(),
            root_path=context_path,
            node_registery=node_registry,
        )
        acl.build_nodes(result.code_documents)

        return node_registry.nodes

@dataclass
class NodeRegistry:
    store_by_fqn: dict[str, CodeNodeDto] = field(default_factory=dict)
    temp_store: dict[str, CodeNodeDto] = field(default_factory=dict)

    @property
    def nodes(self) -> list[CodeNodeDto]:
        return list(self.store_by_fqn.values())

    def get_node(self, fqn: str) -> CodeNodeDto:
        self._ensure_external_node(fqn)
        if fqn in self.store_by_fqn:
            return self.store_by_fqn[fqn]
        if fqn in self.temp_store:
            return self.temp_store[fqn]
        raise ValueError(f"Unknown FQN: {fqn}")

    def find_node(self, fqn: str) -> CodeNodeDto | None:
        return self.store_by_fqn.get(fqn)

    def _ensure_external_node(self, fqn: str) -> None:
        if fqn in self.store_by_fqn:
            return
        if fqn in PythonBuiltinType._value2member_map_:
            self.store_by_fqn[fqn] = ExternalNodeDto(fqn=fqn, name=fqn)
        elif not fqn.startswith("codegen."):
            self.store_by_fqn[fqn] = ExternalNodeDto(fqn=fqn, name=fqn.split(".")[-1])
            
    def add_node(self, dto: CodeNodeDto) -> None:
        if dto.fqn in self.store_by_fqn:
            raise ValueError(f"Duplicate: {dto.fqn=}")
        self.store_by_fqn[dto.fqn] = dto

    def add_temp_node(self, dto: CodeNodeDto) -> None:
        self.temp_store[dto.fqn] = dto

@dataclass
class CodeGraphAcl:
    fqn_factory: FqnFactory
    root_path: Path
    node_registery: NodeRegistry
    overload_index: dict[str, int] = field(default_factory=dict)

    def build_nodes(self, code_documents: list[CodeDocument]) -> list[CodeNodeDto]:
        self._build_directory_nodes(code_documents)
        self._build_file_nodes(code_documents)
        self._build_edges(code_documents=code_documents)

        return self.node_registery.nodes

    def _build_edges(self, code_documents: list[CodeDocument]) -> None:
        for code_document in code_documents:
            module_fqn = self.fqn_factory.build_module_fqn(code_document.physical_path)
            module = self.node_registery.get_node(module_fqn)
            assert isinstance(module, ModuleNodeDto)
            module_builder = ModuleBuildContext(
                module, 
                code_document, 
                self.node_registery
            )
            module_builder.build()
            
    def _add_node(self, dto: CodeNodeDto) -> None:
        self.node_registery.add_node(dto)

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
        fqn = self.fqn_factory.build_dir_fqn(path)
        dto = DirectoryNodeDto(fqn=fqn, name=path.name or fqn)
        parent_fqn = self.fqn_factory.build_dir_fqn(path.parent)
        parent_node = self.node_registery.find_node(parent_fqn)
        if parent_node is not None:
            assert isinstance(parent_node, DirectoryNodeDto)
            parent_node.contains(dto)

        self._add_node(dto)

        return dto

    def _build_file_node(self, code_document: CodeDocument) -> None:
        path = code_document.physical_path
        fqn = self.fqn_factory.build_file_fqn(path)
        file_dto = FileNodeDto(fqn=fqn, name=path.name)

        parent_fqn = self.fqn_factory.build_dir_fqn(path.parent)
        parent_node = self.node_registery.find_node(parent_fqn)
        if parent_node is not None:
            assert isinstance(parent_node, DirectoryNodeDto)
            parent_node.contains(file_dto)

        self._add_node(file_dto)
        self._build_module_node(code_document, file_dto)

    def _build_module_node(
        self, code_document: CodeDocument, file_node: FileNodeDto
    ) -> ModuleNodeDto:
        path = code_document.physical_path
        module_fqn = self.fqn_factory.build_module_fqn(path)
        module_node = ModuleNodeDto(
            fqn=module_fqn,
            name=module_fqn.rsplit(".", maxsplit=1)[-1],
            is_package=path.name == "__init__.py",
        )
        self._add_node(module_node)
        file_node.defines_module(module_node)

        for stmt in code_document.body:
            self._parse_stmt(stmt, module_node)

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
        node = ClassNodeDto(fqn=class_fqn, name=class_def.name)
        module_node.contains(node)
        for stmt in class_def.body:
            self._parse_stmt(stmt, node)

        self._add_node(node)
        return node


    def _parse_function_def(
        self, func_def: AstFunctionDef, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> FunctionNodeDto | MethodNodeDto:
        func_fqn = f"{parent_node.fqn}::{func_def.name}"
        if func_def.is_overload:
            overload_index = self._get_ovrload_index(func_fqn)
            func_fqn = f"{func_fqn}::<overload_{overload_index}>"
        elif func_def.is_setter_property:
            func_fqn = f"{func_fqn}::<setter>"
        elif func_def.is_deleter_property:
            func_fqn = f"{func_fqn}::<deleter>"
        elif func_def.is_expression_property:
            func_fqn = f"{func_fqn}::<expression>"

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


@dataclass
class ModuleBuildContext:
    module: ModuleNodeDto
    code_document: CodeDocument
    node_registery: NodeRegistry
    local_aliases: dict[str, str] = field(init=False)

    def __post_init__(self):
        self.local_aliases = {}
        for edge in self.module.outbound_edges:
            if edge.type is not EdgeType.CONTAINS:
                continue
            target_name = edge.target_fqn.split("::")[-1]
            self.local_aliases[target_name] = edge.target_fqn

    def build(self):
        for stmt in self.code_document.body:
            self._parse_stmt(stmt)
        return self.module

    def _parse_stmt(self, stmt: AstStmt):
        match stmt:
            case AstImport() | AstImportFrom() | AstIf(test=AstName(id="TYPE_CHECKING")):
                self._build_import_edges(stmt)
            case AstClassDef():
                self._parse_class_def(stmt)
            case _:
                pass

    def _build_import_edges(self, stmt: AstStmt) -> None:
        match stmt:
            case AstImport():
                self._parse_import(stmt)
            case AstImportFrom():
                self._parse_import_from(stmt)
            case AstIf(test=AstName(id="TYPE_CHECKING")):
                for subnode in stmt.body:
                    self._build_import_edges(subnode)
            case _:
                pass
                
    def _parse_import(self, import_: AstImport) -> None:
        for name in import_.names:
            self._parse_import_name(name.name, asname=name.asname)
            
    def _parse_import_from(self, import_from: AstImportFrom) -> None:
        if import_from.level > 0:
            relative_level = import_from.level
            if self.module.is_package:
                relative_level = relative_level - 1
            module_prefix = self.module.get_parent_by_level(relative_level)
        else:
            module_prefix = ""

        module = import_from.module or ""
        if module_prefix:
            module = module_prefix + "." + module
        if not module:
            raise ValueError(f"ImportFrom module is empty: {import_from.module}")

        for name in import_from.names:
            self._parse_import_name(
                name.name,
                from_name=module,
                asname=name.asname,
            )
            
    def _parse_import_name(
        self,
        import_name: str,
        from_name: str | None = None,
        asname: str | None = None,
    ) -> None:
        if from_name:
            is_external = not from_name.startswith("codegen.")
        else:
            is_external = not import_name.startswith("codegen.")

        if is_external:
            external_fqn = f"{from_name}.{import_name}" if from_name else import_name
            node = self.node_registery.get_node(external_fqn)
        else:
            node = self._get_internel_node(
                import_name=import_name,
                from_name=from_name,
            )
        assert isinstance(
            node, ExternalNodeDto | ClassNodeDto | FunctionNodeDto | VariableNodeDto
        )
        self.module.imports(node)
        if asname:
            local_alias_key = asname
        else:
            local_alias_key = node.name

        self.local_aliases[local_alias_key] = node.fqn
        
    def _add_node(self, dto: CodeNodeDto) -> None:
        self.node_registery.add_node(dto)
        
    def _get_internel_node(
        self,
        import_name: str,
        from_name: str | None,
    ) -> CodeNodeDto:
        name = import_name
        if from_name is None:
            return self.node_registery.get_node(name)
        module_fqn = f"{from_name}.{name}"
        module_node = self.node_registery.find_node(module_fqn)
        if module_node:
            return module_node
        other_fqn = f"{from_name}::{name}"
        other_node = self.node_registery.find_node(other_fqn)
        if other_node:
            return other_node
        node = ClassNodeDto(
            name=name,
            fqn=other_fqn,
        )
        self.node_registery.add_temp_node(node)
        return node

    def _parse_class_def(self, class_def: AstClassDef) -> None:
        class_fqn = f"{self.module.fqn}::{class_def.name}"
        node = self.node_registery.get_node(class_fqn)
        assert isinstance(node, ClassNodeDto)
        for base in class_def.bases:
            self._parse_base(base, node)

    def _parse_base(
        self,
        base: AstExpr,
        class_node: ClassNodeDto,
    ):
        match base:
            case AstName():
                node_alias_key = base.id
                node_key = self.local_aliases.get(node_alias_key, node_alias_key)
                node = self.node_registery.get_node(node_key)
                assert isinstance(node, (ClassNodeDto, ExternalNodeDto)), node
                class_node.inherits(node)
            case AstSubscript():
                self._parse_base(
                    base=base.value,
                    class_node=class_node,
                )
            case _:
                raise ValueError(f"Unsupported base type: {base}")