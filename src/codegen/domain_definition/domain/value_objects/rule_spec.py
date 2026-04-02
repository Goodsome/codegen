from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.core import ValueObject
from typing import Self


class RuleSpec(ValueObject):
    """BDD rule specification with given/when/then"""

    name: SnakeString
    given: str
    when: str
    then: str

    def to_test_function_spec(self: Self, fixture_name: str) -> FunctionSpec:
        """Map business rule to test function with given/when/then chain."""
        func_name = "test_" + self.name
        fixture_var = VariableSpec.create(
            name=fixture_name,
            type_spec=TypeAnnotationSpec(name=PascalString(fixture_name)),
        )
        chain_suite = (
            f"({fixture_var.name}\n"
            f"    .given({repr(self.given)})\n"
            f"    .arrange_done()\n"
            f"    .when({repr(self.when)})\n"
            f"    .then({repr(self.then)})\n"
            f")"
        )
        return FunctionSpec.create(
            name=func_name,
            parameters=[fixture_var],
            return_annotation=TypeAnnotationSpec(name="None"),
            function_type=FunctionType.FUNCTION,
            suite=chain_suite,
            description=f"[Rule]: {self.name}\n[Desc]: {self.given} -> {self.when} -> {self.then}",
        )
