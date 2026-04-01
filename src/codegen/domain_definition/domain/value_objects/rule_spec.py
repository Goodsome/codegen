from codegen.shared.models import ValueObject
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from typing import Self


class RuleSpec(ValueObject):
    """BDD rule specification with given/when/then"""

    name: PascalString
    given: str
    when: str
    then: str

    def to_test_function_spec(self: Self, fixture_name: str) -> FunctionSpec: ...
