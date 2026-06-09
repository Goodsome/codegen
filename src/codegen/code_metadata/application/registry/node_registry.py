from dataclasses import dataclass, field
from typing import Self

from codegen.code_metadata.domain.aggregates.code_node import (
    CodeNode,
    ExternalNode,
)
from codegen.shared.domain.enums import PythonBuiltinType

@dataclass
class NodeRegistry:
    store_by_fqn: dict[str, CodeNode] = field(default_factory=dict)
    temp_store: dict[str, CodeNode] = field(default_factory=dict)

    @classmethod
    def create(cls, nodes: list[CodeNode]) -> Self:
        return cls(
            store_by_fqn={node.fqn: node for node in nodes},
            temp_store={},
        )

    @property
    def nodes(self) -> list[CodeNode]:
        return list(self.store_by_fqn.values())

    def get_node(self, fqn: str) -> CodeNode:
        self._ensure_external_node(fqn)
        if fqn in self.store_by_fqn:
            return self.store_by_fqn[fqn]
        if fqn in self.temp_store:
            return self.temp_store[fqn]
        raise ValueError(f"Unknown FQN: {fqn}")

    def find_node(self, fqn: str) -> CodeNode | None:
        return self.store_by_fqn.get(fqn)

    def _ensure_external_node(self, fqn: str) -> None:
        if fqn in self.store_by_fqn:
            return
        if fqn in PythonBuiltinType._value2member_map_:
            self.store_by_fqn[fqn] = ExternalNode(fqn=fqn, name=fqn)
        elif not fqn.startswith("codegen."):
            self.store_by_fqn[fqn] = ExternalNode(fqn=fqn, name=fqn.split(".")[-1])
            
    def add_node(self, dto: CodeNode) -> None:
        if dto.fqn in self.store_by_fqn:
            raise ValueError(f"Duplicate: {dto.fqn=}")
        self.store_by_fqn[dto.fqn] = dto

    def add_temp_node(self, dto: CodeNode) -> None:
        self.temp_store[dto.fqn] = dto
