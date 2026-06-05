from dataclasses import dataclass
from typing import cast, override
from uuid import UUID

from sqlalchemy import delete, select, or_
from sqlalchemy.engine import CursorResult
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker

from codegen.code_metadata.application.dtos.bulk_save_result import BulkSaveResult
from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto, ModuleNodeDto
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import CodeNodeModel


@dataclass
class SqlAlchemyCodeNodeSyncService(CodeNodeSyncService):
    """CodeNode 批量同步的 SQLAlchemy 实现。"""

    session_factory: sessionmaker[Session]

    @override
    def save_nodes_bulk(
        self,
        node_dtos: list[CodeNodeDto],
        sync_id: str,
        fqn_prefix: str,
        module_fqn_prefix: str,
    ) -> BulkSaveResult:
        if not node_dtos:
            return BulkSaveResult(nodes_upserted=0, edges_created=0)

        with self.session_factory() as session:
            # ── Phase 1: 批量 UPSERT 节点 (利用 executemany) ──
            node_values = [
                {
                    "fqn": dto.fqn,
                    "kind": dto.kind.value,
                    "name": dto.name,
                    "properties": {"is_package": dto.is_package} if isinstance(dto, ModuleNodeDto) else {},
                    "last_sync_id": sync_id,
                }
                for dto in node_dtos
            ]
            
            stmt = insert(CodeNodeModel)
            stmt = stmt.on_conflict_do_update(
                index_elements=["fqn"],
                set_={
                    "name": stmt.excluded.name,
                    "kind": stmt.excluded.kind,
                    "properties": stmt.excluded.properties,
                    "last_sync_id": stmt.excluded.last_sync_id,
                },
            )
            session.execute(stmt, node_values)

            # ── Phase 2: 混合查询 FQN → ID 映射 (前缀扫描 + 外部节点点查) ──
            external_fqns: set[str] = set()
            for dto in node_dtos:
                for edge in dto.outbound_edges:
                    if not edge.target_fqn.startswith(fqn_prefix):
                        external_fqns.add(edge.target_fqn)

            conditions = [CodeNodeModel.fqn.startswith(fqn_prefix)]
            if external_fqns:
                conditions.append(CodeNodeModel.fqn.in_(external_fqns))

            rows = session.execute(
                select(CodeNodeModel.id, CodeNodeModel.fqn).where(or_(*conditions))
            ).all()
            fqn_to_id: dict[str, UUID] = {fqn: uid for uid, fqn in rows}

            # ── Phase 3: 子查询一键清空当前前缀下的旧出边 ──
            subq = select(CodeNodeModel.id).where(
                or_(
                    CodeNodeModel.fqn.startswith(fqn_prefix),
                    CodeNodeModel.fqn.startswith(module_fqn_prefix),
                )
            ).scalar_subquery()

            session.execute(
                delete(CodeEdgeModel).where(CodeEdgeModel.source_id.in_(subq))
            )

            # ── Phase 4: 批量插入新出边 ──
            edge_values = []
            for dto in node_dtos:
                if not dto.outbound_edges:
                    continue
                    
                source_id = fqn_to_id.get(dto.fqn)
                if not source_id:
                    continue

                for idx, edge_dto in enumerate(dto.outbound_edges):
                    target_id = fqn_to_id.get(edge_dto.target_fqn)
                    if not target_id:
                        continue 
                        
                    edge_values.append({
                        "source_id": source_id,
                        "target_id": target_id,
                        "type": edge_dto.type.value,
                        "position": idx,
                    })
                    
            if edge_values:
                session.execute(insert(CodeEdgeModel), edge_values)

            session.commit()

        return BulkSaveResult(
            nodes_upserted=len(node_values),
            edges_created=len(edge_values),
        )

    @override
    def delete_stale_nodes(
        self,
        fqn_prefix: str,
        current_sync_id: str,
        module_fqn_prefix: str,
    ) -> int:
        with self.session_factory() as session:
            stmt = delete(CodeNodeModel).where(
                or_(
                    CodeNodeModel.fqn.startswith(fqn_prefix),
                    CodeNodeModel.fqn.startswith(module_fqn_prefix),
                ),
                CodeNodeModel.last_sync_id != current_sync_id,
            )
            result = session.execute(stmt)
            session.commit()
            
            # 使用 cast 显式转换为 CursorResult 以消除类型检查器关于 rowcount 的报错
            return cast(CursorResult[int], result).rowcount