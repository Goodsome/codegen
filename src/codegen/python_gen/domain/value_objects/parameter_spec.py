"""
Kind: ValueObject
Name: ParameterSpec
Description: Represents a parameter in a Python function.
"""

from codegen.domain.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class ParameterSpec(ValueObject):
    """Represents a parameter in a Python function."""

    name: str
    annotation: TypeAnnotationSpec
    default: str | None = None
