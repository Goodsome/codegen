from dataclasses import dataclass, field

from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDto,
    ExternalNodeDto,
)
from codegen.shared.domain.enums import PythonBuiltinType

@dataclass
class NodeRegistry:
    store_by_fqn: dict[str, CodeNodeDto] = field(default_factory=dict)
    temp_store: dict[str, CodeNodeDto] = field(default_factory=dict)

    @property
    def nodes(self) -> list[CodeNodeDto]:
        return list(self.store_by_fqn.values())

    def get_node(self, fqn: str) -> CodeNodeDto:
        self._ensure_external_node(fqn)
        if fqn in self.store_by_fqn:
            return self.store_by_fqn[fqn]
        if fqn in self.temp_store:
            return self.temp_store[fqn]
        raise ValueError(f"Unknown FQN: {fqn}")

    def find_node(self, fqn: str) -> CodeNodeDto | None:
        return self.store_by_fqn.get(fqn)

    def _ensure_external_node(self, fqn: str) -> None:
        if fqn in self.store_by_fqn:
            return
        if fqn in PythonBuiltinType._value2member_map_:
            self.store_by_fqn[fqn] = ExternalNodeDto(fqn=fqn, name=fqn)
        elif not fqn.startswith("codegen."):
            self.store_by_fqn[fqn] = ExternalNodeDto(fqn=fqn, name=fqn.split(".")[-1])
            
    def add_node(self, dto: CodeNodeDto) -> None:
        if dto.fqn in self.store_by_fqn:
            raise ValueError(f"Duplicate: {dto.fqn=}")
        self.store_by_fqn[dto.fqn] = dto

    def add_temp_node(self, dto: CodeNodeDto) -> None:
        self.temp_store[dto.fqn] = dto
