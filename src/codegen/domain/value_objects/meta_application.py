"""
Kind: ValueObject
Name: MetaApplication
Description: Specification of an application to be generated.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.meta_use_case import MetaUseCase

from typing import List


class MetaApplication(ValueObject):
    """Specification of an application to be generated."""

    use_cases: List[MetaUseCase]
