from typing import Self
from pydantic import BaseModel, Field

from codegen.code_metadata.application.dtos.file_metrics import FileMetrics


class DevProgress(BaseModel):
    records: list[FileMetrics] = Field(default_factory=list)

    def add_record(self, record: FileMetrics):
        self.records.append(record)

    def filter_by_type(self, component_type: str) -> list[FileMetrics]:
        return [
            record for record in self.records if record.component_type == component_type
        ]

    @property
    def ast_progress(self) -> float:
        if not self.records:
            return 0.0
        return sum(record.ast_similarity for record in self.records) / len(self.records)
        

    def order_by_type(self) -> Self:
        self.records.sort(key=lambda r: r.component_type)
        return self