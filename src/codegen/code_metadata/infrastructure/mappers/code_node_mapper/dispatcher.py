from __future__ import annotations
from typing import assert_never, Any, cast

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto, CodeNodeDetailDto, ModuleNodeDto, VariableNodeDto
from codegen.code_metadata.domain.aggregates.code_node import ClassNode, CodeNode, DirectoryNode, ExternalNode, FileNode, FunctionNode, MethodNode, ModuleNode, VariableNode
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
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
from .base_mapper import BaseMapper
from .directory_node import DirectoryNodeMapper
from .file_node import FileNodeMapper
from .module_node import ModuleNodeMapper
from .class_node import ClassNodeMapper
from .function_node import FunctionNodeMapper
from .method_node import MethodNodeMapper
from .variable_node import VariableNodeMapper
from .external_node import ExternalNodeMapper

def orm_to_domain(orm_model: CodeNodeModel) -> CodeNode:
    """基于 kind 属性进行 match-case 分发，并使用 cast 显式收窄类型"""
    kind = CodeNodeKind(orm_model.kind)
    match kind:
        case CodeNodeKind.DIRECTORY:
            return DirectoryNodeMapper.to_domain(cast(DirectoryNodeModel, orm_model))
        case CodeNodeKind.FILE:
            return FileNodeMapper.to_domain(cast(FileNodeModel, orm_model))
        case CodeNodeKind.MODULE:
            return ModuleNodeMapper.to_domain(cast(ModuleNodeModel, orm_model))
        case CodeNodeKind.CLASS:
            return ClassNodeMapper.to_domain(cast(ClassNodeModel, orm_model))
        case CodeNodeKind.FUNCTION:
            return FunctionNodeMapper.to_domain(cast(FunctionNodeModel, orm_model))
        case CodeNodeKind.METHOD:
            return MethodNodeMapper.to_domain(cast(MethodNodeModel, orm_model))
        case CodeNodeKind.VARIABLE:
            return VariableNodeMapper.to_domain(cast(VariableNodeModel, orm_model))
        case CodeNodeKind.EXTERNAL:
            return ExternalNodeMapper.to_domain(cast(ExternalNodeModel, orm_model))
        case _:
            assert_never(kind)

def orm_to_dto(orm_model: CodeNodeModel) -> CodeNodeDto:
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

def domain_to_orm(domain_entity: CodeNode) -> CodeNodeModel:
    """Domain -> ORM 的显式流转"""
    match domain_entity:
        case DirectoryNode():
            return DirectoryNodeMapper.to_orm(domain_entity)
        case FileNode():
            return FileNodeMapper.to_orm(domain_entity)
        case ModuleNode():
            return ModuleNodeMapper.to_orm(domain_entity)
        case ClassNode():
            return ClassNodeMapper.to_orm(domain_entity)
        case FunctionNode():
            return FunctionNodeMapper.to_orm(domain_entity)
        case MethodNode():
            return MethodNodeMapper.to_orm(domain_entity)
        case VariableNode():
            return VariableNodeMapper.to_orm(domain_entity)
        case ExternalNode():
            return ExternalNodeMapper.to_orm(domain_entity)
        case _:
            assert_never(domain_entity)

def orm_to_detail_dto(orm_model: CodeNodeModel) -> CodeNodeDetailDto:
    return BaseMapper.to_detail_dto(orm_model)

def dto_to_upsert_dict(dto: CodeNodeDto, sync_id: str) -> dict[str, Any]:
    """高性能批量同步分发"""
    match dto:
        case ModuleNodeDto():
            properties = {"is_package": dto.is_package}
        case VariableNodeDto():
            return VariableNodeMapper.dto_to_upsert_dict(dto, sync_id)
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