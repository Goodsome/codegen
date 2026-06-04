from pathlib import Path
from pydantic import BaseModel

from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt


class CodeDocument(BaseModel):
    physical_path: Path
    body: list[AstStmt]