from abc import ABC, abstractmethod
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint


class BlueprintStorage(ABC):
    """Loads the blueprint from a file."""

    @abstractmethod
    def load(self) -> Blueprint | None: ...

    @abstractmethod
    def save(self, blueprint: Blueprint) -> None: ...
