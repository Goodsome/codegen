"""基于 EdgeType 将 ORM 边分发至对应的 Edge Mapper。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, assert_never

from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.code_edge import (
    AcceptsEdge,
    CallsEdge,
    CodeEdge,
    ContainsEdge,
    DefinesEdge,
    DefinesModuleEdge,
    ExportsEdge,
    ImportsEdge,
    ImplementsEdge,
    InheritsEdge,
    ReadsEdge,
    ReturnsEdge,
    TypedAsEdge,
    WritesEdge,
)

from .accepts_edge import AcceptsEdgeMapper
from .calls_edge import CallsEdgeMapper
from .contains_edge import ContainsEdgeMapper
from .defines_edge import DefinesEdgeMapper
from .defines_module_edge import DefinesModuleEdgeMapper
from .exports_edge import ExportsEdgeMapper
from .imports_edge import ImportsEdgeMapper
from .implements_edge import ImplementsEdgeMapper
from .inherits_edge import InheritsEdgeMapper
from .reads_edge import ReadsEdgeMapper
from .returns_edge import ReturnsEdgeMapper
from .typed_as_edge import TypedAsEdgeMapper
from .writes_edge import WritesEdgeMapper

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
        CodeEdgeModel,
    )


def to_dto(edge_model: CodeEdgeModel, direction: EdgeDirection) -> CodeEdge:
    """将单个 ORM 边模型转换为对应类型的 Domain 边值对象。"""
    edge_type = EdgeType(edge_model.type)
    match edge_type:
        case EdgeType.CONTAINS:
            return ContainsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.DEFINES:
            return DefinesEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.DEFINES_MODULE:
            return DefinesModuleEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.IMPORTS:
            return ImportsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.EXPORTS:
            return ExportsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.INHERITS:
            return InheritsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.IMPLEMENTS:
            return ImplementsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.CALLS:
            return CallsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.READS:
            return ReadsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.WRITES:
            return WritesEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.TYPED_AS:
            return TypedAsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.RETURNS:
            return ReturnsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.ACCEPTS:
            return AcceptsEdgeMapper.to_dto(edge_model, direction)
        case _:
            assert_never(edge_type)


def to_outbound_edges(edge_models: list[CodeEdgeModel]) -> list[CodeEdge]:
    """批量转换出边。"""
    return [to_dto(e, EdgeDirection.OUT) for e in edge_models]


def to_inbound_edges(edge_models: list[CodeEdgeModel]) -> list[CodeEdge]:
    """批量转换入边。"""
    return [to_dto(e, EdgeDirection.IN) for e in edge_models]


def code_edge_to_upsert_dict(edge: CodeEdge) -> dict[str, Any]:
    """将 Domain 边值对象转换为可直接用于 INSERT 的 dict（不含 source_id / target_id）。"""
    match edge:
        case ContainsEdge():
            properties = ContainsEdgeMapper.to_properties(edge)
        case DefinesEdge():
            properties = DefinesEdgeMapper.to_properties(edge)
        case DefinesModuleEdge():
            properties = DefinesModuleEdgeMapper.to_properties(edge)
        case ImportsEdge():
            properties = ImportsEdgeMapper.to_properties(edge)
        case ExportsEdge():
            properties = ExportsEdgeMapper.to_properties(edge)
        case InheritsEdge():
            properties = InheritsEdgeMapper.to_properties(edge)
        case ImplementsEdge():
            properties = ImplementsEdgeMapper.to_properties(edge)
        case CallsEdge():
            properties = CallsEdgeMapper.to_properties(edge)
        case ReadsEdge():
            properties = ReadsEdgeMapper.to_properties(edge)
        case WritesEdge():
            properties = WritesEdgeMapper.to_properties(edge)
        case TypedAsEdge():
            properties = TypedAsEdgeMapper.to_properties(edge)
        case ReturnsEdge():
            properties = ReturnsEdgeMapper.to_properties(edge)
        case AcceptsEdge():
            properties = AcceptsEdgeMapper.to_properties(edge)
        case _:
            assert_never(edge)

    return {
        "type": edge.kind.value,
        "properties": properties,
    }
