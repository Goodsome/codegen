from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.code_node_dto import (
    ClassNodeDto,
    CodeNodeDetailDto,
    CodeNodeDto,
    DirectoryNodeDto,
    ExternalNodeDto,
    FileNodeDto,
    FunctionNodeDto,
    MethodNodeDto,
    ModuleNodeDto,
    OutboundEdgeDto,
    VariableNodeDto,
)
from codegen.code_metadata.application.dtos.graph_view import GraphViewDTO, GraphViewNode
from codegen.code_metadata.application.dtos.trace_query import TraceSymbolDependenciesQuery
from codegen.code_metadata.application.ports.code_node_query_service import CodeNodeQueryService
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.enums.trace_direction import TraceDirection


@dataclass
class TraceSymbolDependenciesQueryHandler:
    """CQRS 查询执行器：以 DFS 方式追踪符号的上下游依赖关系。"""

    query_service: CodeNodeQueryService

    _SKIP_EDGE_TYPES: frozenset[EdgeType] = frozenset({
        EdgeType.DEFINES_MODULE,
    })

    def execute(self, query: TraceSymbolDependenciesQuery) -> GraphViewDTO:
        detail = self.query_service.find_by_fqn(query.target_fqn)
        if detail is None:
            raise ValueError(f"Node with fqn '{query.target_fqn}' not found")

        root = self._build_tree(detail, query.direction, visited=set(), edge_type_filter=query.edge_type, depth=query.depth)
        return GraphViewDTO(root=root)

    def _build_tree(
        self,
        detail: CodeNodeDetailDto,
        direction: TraceDirection,
        visited: set[str],
        edge_type_filter: EdgeType | None = None,
        depth: int = 1,
    ) -> GraphViewNode:
        """递归构建以 detail 为根的依赖子树。depth 控制最大递归层数。"""
        visited.add(detail.fqn)

        children: list[GraphViewNode] = []

        if depth > 0:
            edges = detail.outbound_edges if direction == TraceDirection.OUT else detail.inbound_edges
            fqn_attr = "target_fqn" if direction == TraceDirection.OUT else "source_fqn"

            for edge in edges:
                if edge.type in self._SKIP_EDGE_TYPES:
                    continue
                if edge_type_filter is not None and edge.type != edge_type_filter:
                    continue
                next_fqn = getattr(edge, fqn_attr)
                if next_fqn in visited:
                    continue
                child_detail = self.query_service.find_by_fqn(next_fqn)
                if child_detail is None:
                    continue
                child_node = self._build_tree(child_detail, direction, visited, edge_type_filter, depth=depth - 1)
                child_node.edge_type = edge.type
                children.append(child_node)

        return GraphViewNode(node=_detail_to_node_dto(detail), children=children)

    @staticmethod
    def group_children_by_edge_type(
        children: list[GraphViewNode],
    ) -> list[GraphViewNode]:
        """将子节点按 edge_type 分组：CONTAINS 边直接展示，其余归入分组节点。"""
        grouped: dict[EdgeType | None, list[GraphViewNode]] = defaultdict(list)
        for child in children:
            grouped[child.edge_type].append(child)

        result: list[GraphViewNode] = []

        # 无 edge_type 的节点排最前
        result.extend(grouped.pop(None, []))

        # CONTAINS 组的成员直接平铺
        result.extend(grouped.pop(EdgeType.CONTAINS, []))

        # 其余非 CONTAINS 边按类型分组为虚拟节点
        for edge_type in sorted(grouped, key=lambda e: str(e)):
            section = GraphViewNode(
                node=None,  # type: ignore[arg-type]
                edge_type=edge_type,
                children=grouped[edge_type],
            )
            result.append(section)

        return result


def _detail_to_node_dto(detail: CodeNodeDetailDto) -> CodeNodeDto:
    """将 CodeNodeDetailDto 降级为 CodeNodeDto（用于树节点存储）。"""
    outbound_edges = [
        OutboundEdgeDto(type=e.type, target_fqn=e.target_fqn)
        for e in detail.outbound_edges
    ]
    match detail.kind:
        case CodeNodeKind.DIRECTORY:
            return DirectoryNodeDto(fqn=detail.fqn, name=detail.name, outbound_edges=outbound_edges)
        case CodeNodeKind.FILE:
            return FileNodeDto(fqn=detail.fqn, name=detail.name, outbound_edges=outbound_edges)
        case CodeNodeKind.MODULE:
            return ModuleNodeDto(
                fqn=detail.fqn,
                name=detail.name,
                is_package=bool(detail.properties.get("is_package", False)),
                outbound_edges=outbound_edges,
            )
        case CodeNodeKind.CLASS:
            return ClassNodeDto(fqn=detail.fqn, name=detail.name, outbound_edges=outbound_edges)
        case CodeNodeKind.FUNCTION:
            return FunctionNodeDto(fqn=detail.fqn, name=detail.name, outbound_edges=outbound_edges)
        case CodeNodeKind.METHOD:
            return MethodNodeDto(fqn=detail.fqn, name=detail.name, outbound_edges=outbound_edges)
        case CodeNodeKind.VARIABLE:
            return VariableNodeDto(fqn=detail.fqn, name=detail.name, outbound_edges=outbound_edges)
        case CodeNodeKind.EXTERNAL:
            return ExternalNodeDto(fqn=detail.fqn, name=detail.name, outbound_edges=outbound_edges)
