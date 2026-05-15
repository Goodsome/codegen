from dataclasses import dataclass
from typing import override

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.application.ports.component_query_service import (
    ComponentQueryService,
)
from codegen.code_metadata.infrastructure.persistence.mappers.component_mapper import (
    ComponentMapper,
)
from codegen.code_metadata.infrastructure.persistence.models.component_model import (
    ComponentModel,
)


@dataclass
class SQLAlchemyComponentQueryService(ComponentQueryService):
    session_factory: sessionmaker[Session]

    @override
    def find_by_name(self, name: str, context: str) -> ComponentDTO | None:
        stmt = select(ComponentModel).where(
            ComponentModel.name == name, ComponentModel.context == context
        )

        with self.session_factory() as session:
            model = session.execute(stmt).scalar_one_or_none()

        if model is None:
            return None
        dto = ComponentMapper.to_dto(model)
        return dto
