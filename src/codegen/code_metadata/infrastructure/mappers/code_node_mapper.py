from __future__ import annotations
from typing import assert_never

from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDto,
    DirectoryNodeDto,
    FileNodeDto,
    ModuleNodeDto,
    OutboundEdgeDto,
)
from codegen.code_metadata.domain.aggregates.code_node import (
    CodeNode,
    DirectoryNode,
    FileNode,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.domain.value_objects.code_edge import OutboundEdge
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
    DirectoryNodeModel,
    FileNodeModel,
)


class CodeNodeMapper:
    """
    负责 CodeNode 在 ORM、Domain、DTO 三层之间的转换。
    - 单表继承：DirectoryNodeModel / FileNodeModel
    - outbound_edges 通过 CodeEdgeModel 转换
    """

    # ==========================================
    # ORM -> Domain
    # ==========================================

    @classmethod
    def to_domain(cls, orm_model: CodeNodeModel) -> CodeNode:
        match orm_model.kind:
            case CodeNodeKind.DIRECTORY:
                return cls._to_directory_node(orm_model)
            case CodeNodeKind.FILE:
                return cls._to_file_node(orm_model)
            case _:
                raise ValueError(f"Unknown code node kind: {orm_model.kind}")

    @classmethod
    def _to_directory_node(cls, orm_model: CodeNodeModel) -> DirectoryNode:
        assert isinstance(orm_model, DirectoryNodeModel)
        return DirectoryNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=[cls._to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def _to_file_node(cls, orm_model: CodeNodeModel) -> FileNode:
        assert isinstance(orm_model, FileNodeModel)
        return FileNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=[cls._to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def _to_outbound_edge(cls, edge_model: CodeEdgeModel) -> OutboundEdge:
        return OutboundEdge(
            type=EdgeType(edge_model.type),
            target_id=CodeNodeId.reconstitute(edge_model.target_id),
        )

    # ==========================================
    # ORM -> DTO
    # ==========================================

    @classmethod
    def to_dto(cls, orm_model: CodeNodeModel) -> CodeNodeDto:
        edges = [
            OutboundEdgeDto(type=EdgeType(e.type), target_fqn=e.target_entity.fqn)
            for e in orm_model.outbound_edges
        ]
        node_kind = CodeNodeKind(orm_model.kind)
        match node_kind:
            case CodeNodeKind.DIRECTORY:
                return DirectoryNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case CodeNodeKind.FILE:
                return FileNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case CodeNodeKind.MODULE:
                return ModuleNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case _:
                assert_never(node_kind)

    # ==========================================
    # Domain -> ORM
    # ==========================================

    @classmethod
    def to_orm(cls, domain_entity: CodeNode) -> CodeNodeModel:
        match domain_entity.kind:
            case CodeNodeKind.DIRECTORY:
                return cls._directory_to_orm(domain_entity)
            case CodeNodeKind.FILE:
                return cls._file_to_orm(domain_entity)
            case _:
                assert_never(domain_entity.kind)

    @classmethod
    def _directory_to_orm(cls, domain_entity: DirectoryNode) -> DirectoryNodeModel:
        model = DirectoryNodeModel(
            id=domain_entity.id.value,
            fqn=domain_entity.fqn,
            name=domain_entity.name,
        )
        model.outbound_edges = [
            cls._to_edge_model(domain_entity.id, edge)
            for edge in domain_entity.outbound_edges
        ]
        return model

    @classmethod
    def _file_to_orm(cls, domain_entity: FileNode) -> FileNodeModel:
        model = FileNodeModel(
            id=domain_entity.id.value,
            fqn=domain_entity.fqn,
            name=domain_entity.name,
        )
        model.outbound_edges = [
            cls._to_edge_model(domain_entity.id, edge)
            for edge in domain_entity.outbound_edges
        ]
        return model

    @classmethod
    def _to_edge_model(
        cls, source_id: CodeNodeId, edge: OutboundEdge,
    ) -> CodeEdgeModel:
        return CodeEdgeModel(
            source_id=source_id.value,
            target_id=edge.target_id.value,
            type=edge.type.value,
        )
