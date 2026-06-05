from __future__ import annotations
from typing import assert_never

from codegen.code_metadata.application.dtos.code_node_dto import (
    ClassNodeDto,
    CodeNodeDetailDto,
    CodeNodeDto,
    DirectoryNodeDto,
    ExternalNodeDto,
    FileNodeDto,
    FunctionNodeDto,
    InboundEdgeDto,
    MethodNodeDto,
    ModuleNodeDto,
    OutboundEdgeDto,
    VariableNodeDto,
)
from codegen.code_metadata.domain.aggregates.code_node import (
    ClassNode,
    CodeNode,
    DirectoryNode,
    ExternalNode,
    FileNode,
    FunctionNode,
    MethodNode,
    ModuleNode,
    VariableNode,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.domain.value_objects.code_edge import OutboundEdge
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ClassNodeModel,
    CodeNodeModel,
    DirectoryNodeModel,
    ExternalNodeModel,
    FileNodeModel,
    FunctionNodeModel,
    MethodNodeModel,
    ModuleNodeModel,
    VariableNodeModel,
)


class CodeNodeMapper:
    """
    负责 CodeNode 在 ORM、Domain、DTO 三层之间的转换。
    - 单表继承：DirectoryNodeModel / FileNodeModel / ClassNodeModel / FunctionNodeModel / MethodNodeModel / VariableNodeModel / ExternalNodeModel
    - outbound_edges 通过 CodeEdgeModel 转换
    """

    # ==========================================
    # ORM -> Domain
    # ==========================================

    @classmethod
    def to_domain(cls, orm_model: CodeNodeModel) -> CodeNode:
        kind = CodeNodeKind(orm_model.kind)
        match kind:
            case CodeNodeKind.DIRECTORY:
                return cls._to_directory_node(orm_model)
            case CodeNodeKind.FILE:
                return cls._to_file_node(orm_model)
            case CodeNodeKind.MODULE:
                return cls._to_module_node(orm_model)
            case CodeNodeKind.CLASS:
                return cls._to_class_node(orm_model)
            case CodeNodeKind.FUNCTION:
                return cls._to_function_node(orm_model)
            case CodeNodeKind.METHOD:
                return cls._to_method_node(orm_model)
            case CodeNodeKind.VARIABLE:
                return cls._to_variable_node(orm_model)
            case CodeNodeKind.EXTERNAL:
                return cls._to_external_node(orm_model)
            case _:
                assert_never(kind)

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
    def _to_module_node(cls, orm_model: CodeNodeModel) -> ModuleNode:
        assert isinstance(orm_model, ModuleNodeModel)
        return ModuleNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            is_package=orm_model.is_package,
            outbound_edges=[cls._to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def _to_class_node(cls, orm_model: CodeNodeModel) -> ClassNode:
        assert isinstance(orm_model, ClassNodeModel)
        return ClassNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=[cls._to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def _to_function_node(cls, orm_model: CodeNodeModel) -> FunctionNode:
        assert isinstance(orm_model, FunctionNodeModel)
        return FunctionNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=[cls._to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def _to_method_node(cls, orm_model: CodeNodeModel) -> MethodNode:
        assert isinstance(orm_model, MethodNodeModel)
        return MethodNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=[cls._to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def _to_variable_node(cls, orm_model: CodeNodeModel) -> VariableNode:
        assert isinstance(orm_model, VariableNodeModel)
        return VariableNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=[cls._to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def _to_external_node(cls, orm_model: CodeNodeModel) -> ExternalNode:
        assert isinstance(orm_model, ExternalNodeModel)
        return ExternalNode(
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
                assert isinstance(orm_model, ModuleNodeModel)
                return ModuleNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    is_package=orm_model.is_package,
                    outbound_edges=edges,
                )
            case CodeNodeKind.CLASS:
                return ClassNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case CodeNodeKind.FUNCTION:
                return FunctionNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case CodeNodeKind.METHOD:
                return MethodNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case CodeNodeKind.VARIABLE:
                return VariableNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case CodeNodeKind.EXTERNAL:
                return ExternalNodeDto(
                    fqn=orm_model.fqn,
                    name=orm_model.name,
                    outbound_edges=edges,
                )
            case _:
                assert_never(node_kind)

    @classmethod
    def to_detail_dto(cls, orm_model: CodeNodeModel) -> CodeNodeDetailDto:
        """ORM -> 详情 DTO（含入边和出边）。"""
        outbound_edges = [
            OutboundEdgeDto(type=EdgeType(e.type), target_fqn=e.target_entity.fqn)
            for e in orm_model.outbound_edges
        ]
        inbound_edges = [
            InboundEdgeDto(type=EdgeType(e.type), source_fqn=e.source_entity.fqn)
            for e in orm_model.inbound_edges
        ]
        return CodeNodeDetailDto(
            id=orm_model.id,
            fqn=orm_model.fqn,
            name=orm_model.name,
            kind=CodeNodeKind(orm_model.kind),
            description=orm_model.description,
            properties=orm_model.properties,
            outbound_edges=outbound_edges,
            inbound_edges=inbound_edges,
        )

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
            case CodeNodeKind.MODULE:
                return cls._module_to_orm(domain_entity)
            case CodeNodeKind.CLASS:
                return cls._class_to_orm(domain_entity)
            case CodeNodeKind.FUNCTION:
                return cls._function_to_orm(domain_entity)
            case CodeNodeKind.METHOD:
                return cls._method_to_orm(domain_entity)
            case CodeNodeKind.VARIABLE:
                return cls._variable_to_orm(domain_entity)
            case CodeNodeKind.EXTERNAL:
                return cls._external_to_orm(domain_entity)
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
    def _module_to_orm(cls, domain_entity: ModuleNode) -> ModuleNodeModel:
        model = ModuleNodeModel(
            id=domain_entity.id.value,
            fqn=domain_entity.fqn,
            name=domain_entity.name,
        )
        model.is_package = domain_entity.is_package
        model.outbound_edges = [
            cls._to_edge_model(domain_entity.id, edge)
            for edge in domain_entity.outbound_edges
        ]
        return model


    @classmethod
    def _class_to_orm(cls, domain_entity: ClassNode) -> ClassNodeModel:
        model = ClassNodeModel(
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
    def _function_to_orm(cls, domain_entity: FunctionNode) -> FunctionNodeModel:
        model = FunctionNodeModel(
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
    def _method_to_orm(cls, domain_entity: MethodNode) -> MethodNodeModel:
        model = MethodNodeModel(
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
    def _variable_to_orm(cls, domain_entity: VariableNode) -> VariableNodeModel:
        model = VariableNodeModel(
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
    def _external_to_orm(cls, domain_entity: ExternalNode) -> ExternalNodeModel:
        model = ExternalNodeModel(
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
