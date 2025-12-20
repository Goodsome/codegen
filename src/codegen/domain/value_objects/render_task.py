"""
Kind: ValueObject
Name: RenderTask
Description: Task for rendering templates with context data.
"""

from codegen.domain.shared.models import ValueObject

from typing import Any, Dict


class RenderTask(ValueObject):
    """Task for rendering templates with context data."""

    target_path: str

    template_name: str

    context_data: Dict[str, Any]
