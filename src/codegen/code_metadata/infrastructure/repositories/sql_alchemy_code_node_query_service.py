from dataclasses import dataclass
from typing import override
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto, CodeNodeDetailDto
from codegen.code_metadata.application.ports.code_node_query_service import CodeNodeQueryService
from codegen.code_metadata.infrastructure.mappers.code_node_mapper import CodeNodeMapper
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import CodeEdgeModel
from codegen.code_metadata.infrastructure.orm_models.code_node_model import CodeNodeModel


@dataclass
class SqlAlchemyCodeNodeQueryService(CodeNodeQueryService):
    session_factory: sessionmaker[Session]

    @override
    def find_by_fqn_prefix(self, fqn_prefix: str) -> list[CodeNodeDto]:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.fqn.like(f"{fqn_prefix}%"))
            .options(
                selectinload(CodeNodeModel.outbound_edges)
                .joinedload(CodeEdgeModel.target_entity)
            )
        )

        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()

        return [CodeNodeMapper.to_dto(m) for m in models]

    @override
    def find_by_id(self, node_id: UUID) -> CodeNodeDetailDto | None:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.id == node_id)
            .options(
                selectinload(CodeNodeModel.outbound_edges)
                .joinedload(CodeEdgeModel.target_entity),
                selectinload(CodeNodeModel.inbound_edges)
                .joinedload(CodeEdgeModel.source_entity),
            )
        )

        with self.session_factory() as session:
            model = session.execute(stmt).scalars().unique().one_or_none()

        if model is None:
            return None

        return CodeNodeMapper.to_detail_dto(model)
