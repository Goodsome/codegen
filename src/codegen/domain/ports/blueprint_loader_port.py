from abc import ABC, abstractmethod

from codegen.domain.aggregates.blueprint import Blueprint


class BlueprintLoaderPort(ABC):
    """
    Loads the blueprint from a file.
    """

    @abstractmethod
    def load(self, source: str) -> Blueprint | None:
        pass
