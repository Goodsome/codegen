from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType


class OutboundEdgeDto(BaseModel):
    """边的 DTO：用 target_fqn 引用目标节点，而非 target_id。

    在构建阶段目标节点的数据库 ID 尚不可知，
    因此通过自然键（FQN）建立引用，由仓储层在持久化时解析为实际 ID。
    """

    type: EdgeType
    target_fqn: str


class InboundEdgeDto(BaseModel):
    """入边 DTO：用 source_fqn 引用源节点。"""

    type: EdgeType
    source_fqn: str


class _BaseNodeDto(BaseModel):
    fqn: str
    name: str
    outbound_edges: list[OutboundEdgeDto] = Field(default_factory=list)

    def _add_edge(self, type: EdgeType, fqn: str):
        if any(e.target_fqn == fqn for e in self.outbound_edges):
            return
        self.outbound_edges.append(OutboundEdgeDto(type=type, target_fqn=fqn))

    def add_edge(self, type: EdgeType, node: CodeNodeDto):
        self._add_edge(type, node.fqn)


class DirectoryNodeDto(_BaseNodeDto):
    """目录节点的 DTO：kind 固定为 DIRECTORY。"""

    kind: Literal[CodeNodeKind.DIRECTORY] = CodeNodeKind.DIRECTORY

    def contains(self, node: FileNodeDto | DirectoryNodeDto):
        self._add_edge(EdgeType.CONTAINS, node.fqn)


class FileNodeDto(_BaseNodeDto):
    """文件节点的 DTO：kind 固定为 FILE。"""

    kind: Literal[CodeNodeKind.FILE] = CodeNodeKind.FILE

    def defines_module(self, node: ModuleNodeDto):
        self._add_edge(EdgeType.DEFINES_MODULE, node.fqn)


class ModuleNodeDto(_BaseNodeDto):
    """模块节点的 DTO：kind 固定为 MODULE，由文件节点自动派生。"""

    kind: Literal[CodeNodeKind.MODULE] = CodeNodeKind.MODULE
    is_package: bool = False

    def contains(self, node: ClassNodeDto | FunctionNodeDto | VariableNodeDto):
        self._add_edge(EdgeType.CONTAINS, node.fqn)

    def imports(self, node: ExternalNodeDto | ClassNodeDto | FunctionNodeDto | VariableNodeDto):
        self._add_edge(EdgeType.IMPORTS, node.fqn)

    def get_parent_by_level(self, level: int) -> str:
        if level == 0:
            return self.fqn
        parts = self.fqn.split(".")
        if level >= len(parts):
            raise ValueError(f"Level {level} is greater than the depth of the module {self.fqn}")
        return ".".join(parts[:-level])


class ClassNodeDto(_BaseNodeDto):
    """类节点的 DTO：kind 固定为 CLASS，由模块节点的 AST 类定义派生。"""

    kind: Literal[CodeNodeKind.CLASS] = CodeNodeKind.CLASS

    def contains(self, node: MethodNodeDto | VariableNodeDto):
        self._add_edge(EdgeType.CONTAINS, node.fqn)

    def inherits(self, node: ClassNodeDto | ExternalNodeDto):
        self._add_edge(EdgeType.INHERITS, node.fqn)


class FunctionNodeDto(_BaseNodeDto):
    """函数节点的 DTO：kind 固定为 FUNCTION，由模块节点的 AST 函数定义派生。"""

    kind: Literal[CodeNodeKind.FUNCTION] = CodeNodeKind.FUNCTION

    def returns(self, node: ClassNodeDto | ExternalNodeDto | VariableNodeDto):
        self._add_edge(EdgeType.RETURNS, node.fqn)


class MethodNodeDto(_BaseNodeDto):
    """方法节点的 DTO：kind 固定为 METHOD，由类节点的 AST 函数定义派生。"""

    kind: Literal[CodeNodeKind.METHOD] = CodeNodeKind.METHOD

    def returns(self, node: ClassNodeDto | ExternalNodeDto | VariableNodeDto):
        self._add_edge(EdgeType.RETURNS, node.fqn)

class VariableNodeDto(_BaseNodeDto):
    """变量节点的 DTO：kind 固定为 VARIABLE，由模块节点的 AST 赋值语句派生。"""

    kind: Literal[CodeNodeKind.VARIABLE] = CodeNodeKind.VARIABLE


class ExternalNodeDto(_BaseNodeDto):
    """外部节点的 DTO：kind 固定为 EXTERNAL，表示项目外部的依赖（第三方库、标准库等）。"""

    kind: Literal[CodeNodeKind.EXTERNAL] = CodeNodeKind.EXTERNAL


CodeNodeDto = Annotated[
    DirectoryNodeDto
    | FileNodeDto
    | ModuleNodeDto
    | ClassNodeDto
    | FunctionNodeDto
    | MethodNodeDto
    | VariableNodeDto
    | ExternalNodeDto,
    Field(discriminator="kind"),
]


class CodeNodeDetailDto(BaseModel):
    """CodeNode 详情 DTO：包含 id、基本信息、出边和入边。"""

    id: UUID
    fqn: str
    name: str
    kind: CodeNodeKind
    description: str | None
    properties: dict[str, object]
    outbound_edges: list[OutboundEdgeDto] = Field(default_factory=list)
    inbound_edges: list[InboundEdgeDto] = Field(default_factory=list)
