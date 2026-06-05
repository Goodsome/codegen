from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias
from uuid import UUID

from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType


@dataclass
class OutboundEdgeDto:
    """边的 DTO：用 target_fqn 引用目标节点，而非 target_id。

    在构建阶段目标节点的数据库 ID 尚不可知，
    因此通过自然键（FQN）建立引用，由仓储层在持久化时解析为实际 ID。
    """

    type: EdgeType
    target_fqn: str


@dataclass
class InboundEdgeDto:
    """入边 DTO：用 source_fqn 引用源节点。"""

    type: EdgeType
    source_fqn: str


@dataclass
class _BaseNodeDto:
    fqn: str
    name: str
    outbound_edges: list[OutboundEdgeDto] = field(default_factory=list)

    def _add_edge(self, type: EdgeType, fqn: str):
        if any(e.target_fqn == fqn for e in self.outbound_edges):
            raise ValueError(f"Edge to {fqn} already exists")
        self.outbound_edges.append(OutboundEdgeDto(type=type, target_fqn=fqn))


@dataclass
class DirectoryNodeDto(_BaseNodeDto):
    """目录节点的 DTO：kind 固定为 DIRECTORY。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.DIRECTORY, init=False)

    def contains(self, node: FileNodeDto | DirectoryNodeDto):
        self._add_edge(EdgeType.CONTAINS, node.fqn)


@dataclass
class FileNodeDto(_BaseNodeDto):
    """文件节点的 DTO：kind 固定为 FILE。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.FILE, init=False)

    def defines_module(self, node: ModuleNodeDto):
        self._add_edge(EdgeType.DEFINES_MODULE, node.fqn)


@dataclass
class ModuleNodeDto(_BaseNodeDto):
    """模块节点的 DTO：kind 固定为 MODULE，由文件节点自动派生。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.MODULE, init=False)

    def contains(self, node: ClassNodeDto | FunctionNodeDto | VariableNodeDto):
        self._add_edge(EdgeType.CONTAINS, node.fqn)


@dataclass
class ClassNodeDto(_BaseNodeDto):
    """类节点的 DTO：kind 固定为 CLASS，由模块节点的 AST 类定义派生。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.CLASS, init=False)

    def contains(self, node: MethodNodeDto | VariableNodeDto):
        self._add_edge(EdgeType.CONTAINS, node.fqn)


@dataclass
class FunctionNodeDto(_BaseNodeDto):
    """函数节点的 DTO：kind 固定为 FUNCTION，由模块节点的 AST 函数定义派生。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.FUNCTION, init=False)


@dataclass
class MethodNodeDto(_BaseNodeDto):
    """方法节点的 DTO：kind 固定为 METHOD，由类节点的 AST 函数定义派生。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.METHOD, init=False)


@dataclass
class VariableNodeDto(_BaseNodeDto):
    """变量节点的 DTO：kind 固定为 VARIABLE，由模块节点的 AST 赋值语句派生。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.VARIABLE, init=False)


@dataclass
class ExternalNodeDto(_BaseNodeDto):
    """外部节点的 DTO：kind 固定为 EXTERNAL，表示项目外部的依赖（第三方库、标准库等）。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.EXTERNAL, init=False)


CodeNodeDto: TypeAlias = (
    DirectoryNodeDto
    | FileNodeDto
    | ModuleNodeDto
    | ClassNodeDto
    | FunctionNodeDto
    | MethodNodeDto
    | VariableNodeDto
    | ExternalNodeDto
)


@dataclass
class CodeNodeDetailDto:
    """CodeNode 详情 DTO：包含 id、基本信息、出边和入边。"""

    id: UUID
    fqn: str
    name: str
    kind: CodeNodeKind
    description: str | None
    properties: dict[str, object]
    outbound_edges: list[OutboundEdgeDto] = field(default_factory=list)
    inbound_edges: list[InboundEdgeDto] = field(default_factory=list)
