from pathlib import Path
from pydantic import BaseModel


class FileMetrics(BaseModel):
    file_path: Path
    component_type: str
    ast_similarity: float
    original_lines: int
    generated_lines: int

    @property
    def line_diff(self) -> int:
        return self.generated_lines - self.original_lines