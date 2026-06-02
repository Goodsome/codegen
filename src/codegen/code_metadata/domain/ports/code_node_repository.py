from abc import ABC, abstractmethod

from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.shared.domain.ports.repository import Repository


class CodeNodeRepository(Repository[CodeNode, CodeNodeId], ABC):

    @abstractmethod
    def find_by_ids(self, ids: list[CodeNodeId]) -> dict[CodeNodeId, CodeNode]: ...

    @abstractmethod
    def find_by_fqn(self, fqn: str) -> CodeNode | None: ...

    @abstractmethod
    def find_by_fqns(self, fqns: set[str]) -> dict[str, CodeNode]: ...
