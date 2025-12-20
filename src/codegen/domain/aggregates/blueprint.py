"""
Kind: Aggregate
Name: Blueprint
Description: Root of the generation model. Represents the entire project definition.
"""

from codegen.domain.shared.models import AggregateRoot

from codegen.domain.value_objects.bounded_context import BoundedContext
from codegen.domain.value_objects.meta_bootstrap import MetaBootstrap
from typing import List

class Blueprint(AggregateRoot):
    """Root of the generation model. Represents the entire project definition."""

    name: str
    description: str
    layout: str
    contexts: List[BoundedContext]
    bootstrap: MetaBootstrap

