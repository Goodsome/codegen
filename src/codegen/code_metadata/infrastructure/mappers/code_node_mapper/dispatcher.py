from __future__ import annotations
from typing import assert_never, Any, cast

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto, CodeNodeDetailDto, ModuleNodeDto, VariableNodeDto
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