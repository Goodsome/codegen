from codegen.shared.infrastructure.orm import BaseORM
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID


class TestModel(BaseORM):
    
    __tablename__: str = "test_table"

    id: Mapped[UUID] = mapped_column(primary_key=True)
