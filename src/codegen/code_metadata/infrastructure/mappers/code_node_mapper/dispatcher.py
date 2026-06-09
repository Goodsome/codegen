from __future__ import annotations
from typing import assert_never, Any, cast

from codegen.code_metadata.application.dtos.code_node_detail_dto import CodeNodeDetailDto
from codegen.code_metadata.domain.aggregates.code_node import ClassNode, CodeNode, ModuleNode, VariableNode
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.code_edge import create_edge
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
    DirectoryNodeModel,
    FileNodeModel,
    ModuleNodeModel,
    ClassNodeModel,
    FunctionNodeModel,
    MethodNodeModel,
    VariableNodeModel,
    ExternalNodeModel,
)

# 导入具体的子 Mapper
from .directory_node import DirectoryNodeMapper
from .file_node import FileNodeMapper
from .module_node import ModuleNodeMapper
from .class_node import ClassNodeMapper
from .function_node import FunctionNodeMapper
from .method_node import MethodNodeMapper
from .variable_node import VariableNodeMapper
from .external_node import ExternalNodeMapper


def orm_to_dto(orm_model: CodeNodeModel) -> CodeNode:
    """基于 kind 属性将 ORM 模型安全分发至 DTO 转换逻辑"""
    kind = CodeNodeKind(orm_model.kind)
    match kind:
        case CodeNodeKind.DIRECTORY:
            return DirectoryNodeMapper.to_dto(cast(DirectoryNodeModel, orm_model))
        case CodeNodeKind.FILE:
            return FileNodeMapper.to_dto(cast(FileNodeModel, orm_model))
        case CodeNodeKind.MODULE:
            return ModuleNodeMapper.to_dto(cast(ModuleNodeModel, orm_model))
        case CodeNodeKind.CLASS:
            return ClassNodeMapper.to_dto(cast(ClassNodeModel, orm_model))
        case CodeNodeKind.FUNCTION:
            return FunctionNodeMapper.to_dto(cast(FunctionNodeModel, orm_model))
        case CodeNodeKind.METHOD:
            return MethodNodeMapper.to_dto(cast(MethodNodeModel, orm_model))
        case CodeNodeKind.VARIABLE:
            return VariableNodeMapper.to_dto(cast(VariableNodeModel, orm_model))
        case CodeNodeKind.EXTERNAL:
            return ExternalNodeMapper.to_dto(cast(ExternalNodeModel, orm_model))
        case _:
            assert_never(kind)

def orm_to_detail_dto(orm_model: CodeNodeModel) -> CodeNodeDetailDto:
    outbound_edges = [
        create_edge(EdgeType(e.type), e.target_entity.fqn, EdgeDirection.OUT)
        for e in orm_model.outbound_edges
    ]
    inbound_edges = [
        create_edge(EdgeType(e.type), e.source_entity.fqn, EdgeDirection.IN)
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

def dto_to_upsert_dict(dto: CodeNode, sync_id: str) -> dict[str, Any]:
    """高性能批量同步分发"""
    match dto:
        case ModuleNode():
            properties = {"is_package": dto.is_package}
        case VariableNode():
            properties = VariableNodeMapper.to_properties(dto)
        case ClassNode():
            properties = ClassNodeMapper.to_properties(dto)
        case _:
            properties = {}

    return {
        "fqn": dto.fqn,
        "kind": dto.kind.value,
        "name": dto.name,
        "description": dto.description,
        "properties": properties,
        "last_sync_id": sync_id,
    }