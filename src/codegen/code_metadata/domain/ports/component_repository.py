from abc import ABC

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.ports.repository import Repository


class ComponentRepository(Repository[Component, ComponentId], ABC):
    """Component repository interface."""

    ...
