from dataclasses import dataclass
from typing import override
from uuid import UUID

from sqlalchemy import exists, not_, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from codegen.code_metadata.application.dtos.code_node_detail_dto import CodeNodeDetailDto
from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDto,
)
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.infrastructure.mappers.code_node_mapper import orm_to_detail_dto, orm_to_dto
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)


@dataclass
class SqlAlchemyCodeNodeQueryService(CodeNodeQueryService):
    session_factory: sessionmaker[Session]

    @override
    def find_by_fqn_prefix(self, fqn_prefix: str) -> list[CodeNodeDto]:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.fqn.like(f"{fqn_prefix}%"))
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )

        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()

        return [orm_to_dto(m) for m in models]

    @override
    def find_by_fqn(self, fqn: str) -> CodeNodeDetailDto | None:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.fqn == fqn)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                ),
                selectinload(CodeNodeModel.inbound_edges).joinedload(
                    CodeEdgeModel.source_entity
                ),
            )
        )

        with self.session_factory() as session:
            model = session.execute(stmt).scalars().unique().one_or_none()

        if model is None:
            return None

        return orm_to_detail_dto(model)

    @override
    def find_by_id(self, node_id: UUID) -> CodeNodeDetailDto | None:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.id == node_id)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                ),
                selectinload(CodeNodeModel.inbound_edges).joinedload(
                    CodeEdgeModel.source_entity
                ),
            )
        )

        with self.session_factory() as session:
            model = session.execute(stmt).scalars().unique().one_or_none()

        if model is None:
            return None

        return orm_to_detail_dto(model)

    @override
    def find_unused_nodes(self, kind: CodeNodeKind) -> list[CodeNodeDto]:
        _SUPPORTED = {CodeNodeKind.CLASS, CodeNodeKind.FUNCTION, CodeNodeKind.VARIABLE}
        if kind not in _SUPPORTED:
            raise ValueError(
                f"Unsupported node kind for unused query: {kind}. "
                f"Supported: {', '.join(k.value.lower() for k in sorted(_SUPPORTED))}"
            )

        # 不存在 IMPORTS 或 INHERITS 类型的入边即视为"未被使用"
        _USAGE_EDGE_TYPES = {
            EdgeType.IMPORTS,
            EdgeType.INHERITS,
            EdgeType.CALLS,
            EdgeType.RETURNS,
            EdgeType.ACCEPTS,
            EdgeType.TYPED_AS
        }
        has_usage_inbound = exists().where(
            CodeEdgeModel.target_id == CodeNodeModel.id,
            CodeEdgeModel.type.in_(_USAGE_EDGE_TYPES),
        )
        stmt = (
            select(CodeNodeModel)
            .where(
                CodeNodeModel.kind == kind,
                not_(has_usage_inbound),
            )
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                ),
            )
        )

        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()

        return [orm_to_dto(m) for m in models]
