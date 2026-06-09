from __future__ import annotations

from pathlib import Path
import re
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects import AstExpr
from codegen.code_metadata.domain.value_objects.code_edge import CodeEdge, create_edge


class _BaseNode(BaseModel):
    fqn: str
    name: str
    description: str | None = Field(default=None)
    outbound_edges: list[CodeEdge] = Field(default_factory=list)

    def _add_edge(self, type: EdgeType, fqn: str) -> CodeEdge:
        for e in self.outbound_edges:
            if e.fqn == fqn and e.kind == type:
                return e
        edge = create_edge(kind=type, fqn=fqn, direction=EdgeDirection.OUT)
        self.outbound_edges.append(edge)
        return edge

    def add_edge(self, type: EdgeType, node: CodeNode):
        self._add_edge(type, node.fqn)

    def parent_fqn(self) -> str:
        splits = re.split(r"[.|::]", self.fqn)
        return ".".join(splits[:-1])

class DirectoryNode(_BaseNode):
    """目录节点：kind 固定为 DIRECTORY。"""

    kind: Literal[CodeNodeKind.DIRECTORY] = CodeNodeKind.DIRECTORY

    def contains(self, node: FileNode | DirectoryNode):
        self._add_edge(EdgeType.CONTAINS, node.fqn)


class FileNode(_BaseNode):
    """文件节点：kind 固定为 FILE。"""

    kind: Literal[CodeNodeKind.FILE] = CodeNodeKind.FILE

    def defines_module(self, node: ModuleNode):
        self._add_edge(EdgeType.DEFINES_MODULE, node.fqn)


class ModuleNode(_BaseNode):
    """模块节点：kind 固定为 MODULE，由文件节点自动派生。"""

    kind: Literal[CodeNodeKind.MODULE] = CodeNodeKind.MODULE
    is_package: bool = False

    def contains(self, node: ClassNode | FunctionNode | VariableNode):
        self._add_edge(EdgeType.CONTAINS, node.fqn)

    def imports(self, node: ExternalNode | ClassNode | FunctionNode | VariableNode) -> CodeEdge:
        return self._add_edge(EdgeType.IMPORTS, node.fqn)

    def get_parent_by_level(self, level: int) -> str:
        if level == 0:
            return self.fqn
        parts = self.fqn.split(".")
        if level >= len(parts):
            raise ValueError(f"Level {level} is greater than the depth of the module {self.fqn}")
        return ".".join(parts[:-level])

    def get_physical_path(self) -> Path:
        return Path(self.fqn.replace(".", "/"))


class ClassNode(_BaseNode):
    """类节点：kind 固定为 CLASS，由模块节点的 AST 类定义派生。"""

    kind: Literal[CodeNodeKind.CLASS] = CodeNodeKind.CLASS

    def contains(self, node: MethodNode | VariableNode):
        self._add_edge(EdgeType.CONTAINS, node.fqn)

    def inherits(self, node: ClassNode | ExternalNode):
        self._add_edge(EdgeType.INHERITS, node.fqn)


class FunctionNode(_BaseNode):
    """函数节点：kind 固定为 FUNCTION，由模块节点的 AST 函数定义派生。"""

    kind: Literal[CodeNodeKind.FUNCTION] = CodeNodeKind.FUNCTION

    def contains(self, node: VariableNode):
        self._add_edge(EdgeType.CONTAINS, node.fqn)

    def returns(self, node: ClassNode | ExternalNode | VariableNode):
        self._add_edge(EdgeType.RETURNS, node.fqn)


class MethodNode(_BaseNode):
    """方法节点：kind 固定为 METHOD，由类节点的 AST 函数定义派生。"""

    kind: Literal[CodeNodeKind.METHOD] = CodeNodeKind.METHOD

    def contains(self, node: VariableNode):
        self._add_edge(EdgeType.CONTAINS, node.fqn)

    def returns(self, node: ClassNode | ExternalNode | VariableNode):
        self._add_edge(EdgeType.RETURNS, node.fqn)

class VariableNode(_BaseNode):
    """变量节点：kind 固定为 VARIABLE，由模块节点的 AST 赋值语句派生。"""

    kind: Literal[CodeNodeKind.VARIABLE] = CodeNodeKind.VARIABLE

    annotation: AstExpr | None = None
    value: AstExpr | None = None


class ExternalNode(_BaseNode):
    """外部节点：kind 固定为 EXTERNAL，表示项目外部的依赖（第三方库、标准库等）。"""

    kind: Literal[CodeNodeKind.EXTERNAL] = CodeNodeKind.EXTERNAL


CodeNode = Annotated[
    DirectoryNode
    | FileNode
    | ModuleNode
    | ClassNode
    | FunctionNode
    | MethodNode
    | VariableNode
    | ExternalNode,
    Field(discriminator="kind"),
]
