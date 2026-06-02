from dataclasses import dataclass
from typing import override

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.code_metadata.infrastructure.mappers.code_node_mapper import CodeNodeMapper
from codegen.code_metadata.infrastructure.orm_models.code_node_model import CodeNodeModel


@dataclass
class SqlAlchemyCodeNodeRepository(CodeNodeRepository):
    """
    CodeNode 仓储的 SQLAlchemy 实现。
    负责管理 CodeNode 聚合根的持久化生命周期，隔离基础设施层与领域层。
    """

    session: Session

    def _eager_load(self):
        """返回带有 eager loading 的查询语句"""
        return select(CodeNodeModel).options(
            selectinload(CodeNodeModel.outbound_edges)
        )

    @override
    def _add(self, aggregate: CodeNode) -> None:
        orm_model = CodeNodeMapper.to_orm(aggregate)
        self.session.add(orm_model)

    @override
    def _add_all(self, aggregates: list[CodeNode]) -> None:
        orm_models = [CodeNodeMapper.to_orm(a) for a in aggregates]
        self.session.add_all(orm_models)

    @override
    def _get(self, id: CodeNodeId) -> CodeNode:
        stmt = self._eager_load().where(CodeNodeModel.id == id.value)
        orm_model = self.session.execute(stmt).scalars().first()
        if orm_model is None:
            raise ValueError(f"CodeNode with id {id.value} not found")
        return CodeNodeMapper.to_domain(orm_model)

    @override
    def _save(self, aggregate: CodeNode) -> None:
        orm_model = CodeNodeMapper.to_orm(aggregate)
        self.session.merge(orm_model)

    @override
    def _save_all(self, aggregates: list[CodeNode]) -> None:
        if not aggregates:
            return
        orm_models = [CodeNodeMapper.to_orm(a) for a in aggregates]
        for orm_model in orm_models:
            self.session.merge(orm_model)

    @override
    def _delete(self, id: CodeNodeId) -> None:
        model = self.session.get(CodeNodeModel, id.value)
        if model:
            self.session.delete(model)

    # ==========================================
    # 额外查询方法
    # ==========================================

    @override
    def find_by_ids(self, ids: list[CodeNodeId]) -> dict[CodeNodeId, CodeNode]:
        if not ids:
            return {}
        unique_ids = {id.value for id in ids}
        stmt = self._eager_load().where(CodeNodeModel.id.in_(unique_ids))
        models = self.session.execute(stmt).scalars().unique().all()
        return {
            CodeNodeId.reconstitute(m.id): CodeNodeMapper.to_domain(m)
            for m in models
        }

    @override
    def find_by_fqn(self, fqn: str) -> CodeNode | None:
        stmt = self._eager_load().where(CodeNodeModel.fqn == fqn)
        orm_model = self.session.execute(stmt).scalars().first()
        if orm_model is None:
            return None
        return CodeNodeMapper.to_domain(orm_model)

    @override
    def find_by_fqns(self, fqns: set[str]) -> dict[str, CodeNode]:
        if not fqns:
            return {}
        stmt = self._eager_load().where(CodeNodeModel.fqn.in_(fqns))
        models = self.session.execute(stmt).scalars().unique().all()
        return {m.fqn: CodeNodeMapper.to_domain(m) for m in models}
