"""
Kind: ValueObject
Name: MetaUseCase
Description: Specification of a use case to be generated.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from codegen.domain.value_objects.meta_use_case_command import MetaUseCaseCommand

from codegen.domain.value_objects.meta_use_case_result import MetaUseCaseResult

from typing import List


class MetaUseCase(ValueObject):
    """Specification of a use case to be generated."""

    name: str

    attributes: List[Attribute]

    kind: str

    description: str

    command: MetaUseCaseCommand

    result: MetaUseCaseResult
