"""
Kind: Aggregate
Name: Blueprint
Description: Root of the generation model. Represents the entire project definition.
"""

from codegen.domain.shared.models import AggregateRoot

from codegen.domain.value_objects.bounded_context import BoundedContext

from typing import List


class Blueprint(AggregateRoot):
    """Root of the generation model. Represents the entire project definition."""

    name: str

    layout: str

    contexts: List[BoundedContext]



    def load_from_dict(self):
        pass

