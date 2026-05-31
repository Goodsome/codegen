from pydantic import BaseModel

from codegen.code_metadata.domain.enums.module_kind import ModuleKind


class ModuleDto(BaseModel):
    name: str
    path: str
    kind: ModuleKind
    dir_module_id: str | None