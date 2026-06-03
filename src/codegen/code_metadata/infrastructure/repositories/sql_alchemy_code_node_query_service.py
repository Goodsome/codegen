from dataclasses import dataclass
from typing import override

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto, OutboundEdgeDto
from codegen.code_metadata.application.ports.code_node_query_service import CodeNodeQueryService
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
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

        return [self._to_dto(m) for m in models]

    @classmethod
    def _to_dto(cls, model: CodeNodeModel) -> CodeNodeDto:
        edges = [
            OutboundEdgeDto(type=EdgeType(e.type), target_fqn=e.target_entity.fqn)
            for e in model.outbound_edges
        ]
        return CodeNodeDto(
            fqn=model.fqn,
            name=model.name,
            kind=CodeNodeKind(model.kind),
            outbound_edges=edges,
        )
