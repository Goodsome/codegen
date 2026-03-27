import unittest

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.enums import AssignmentFlavor
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.enums import ContainerType


class TestAttributeSpecLiterals(unittest.TestCase):
    """Test that to_variable_spec() correctly handles literal values (bool, int, float, None)
    vs string code expressions."""

    def test_to_variable_spec_with_false_default(self):
        """When default=False (bool), should use from_literal, not from_code."""
        spec = AttributeSpec(
            name=SnakeString("is_active"),
            type="bool",
            default=False,
            optional=False,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.LITERAL)
        self.assertIs(result.assignment.literal.value, False)

    def test_to_variable_spec_with_true_default(self):
        """When default=True (bool), should use from_literal, not from_code."""
        spec = AttributeSpec(
            name=SnakeString("is_enabled"),
            type="bool",
            default=True,
            optional=False,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.LITERAL)
        self.assertIs(result.assignment.literal.value, True)

    def test_to_variable_spec_with_none_default(self):
        """When default=None, should use from_literal."""
        spec = AttributeSpec(
            name=SnakeString("description"),
            type="str",
            default=None,
            optional=True,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.LITERAL)
        self.assertIsNone(result.assignment.literal.value)

    def test_to_variable_spec_with_int_default_zero(self):
        """When default=0 (int), should use from_literal, not from_code."""
        spec = AttributeSpec(
            name=SnakeString("count"),
            type="int",
            default=0,
            optional=False,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.LITERAL)
        self.assertEqual(result.assignment.literal.value, 0)

    def test_to_variable_spec_with_int_default_positive(self):
        """When default=42 (int), should use from_literal."""
        spec = AttributeSpec(
            name=SnakeString("max_retries"),
            type="int",
            default=42,
            optional=False,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.LITERAL)
        self.assertEqual(result.assignment.literal.value, 42)

    def test_to_variable_spec_with_float_default(self):
        """When default=3.14 (float), should use from_literal."""
        spec = AttributeSpec(
            name=SnakeString("rate"),
            type="float",
            default=3.14,
            optional=False,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.LITERAL)
        self.assertAlmostEqual(result.assignment.literal.value, 3.14)

    def test_to_variable_spec_with_string_default_empty(self):
        """When default="" (empty string), should use from_literal with empty string."""
        spec = AttributeSpec(
            name=SnakeString("name"),
            type="str",
            default="",
            optional=True,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.LITERAL)
        self.assertEqual(result.assignment.literal.value, "")

    def test_to_variable_spec_with_string_default_non_empty(self):
        """When default="some_value" (non-empty string), should use from_code (CODE flavor)."""
        spec = AttributeSpec(
            name=SnakeString("name"),
            type="str",
            default="some_value",
            optional=False,
            container=ContainerType.NONE,
            custom_type_string=None,
        )
        result = spec.to_variable_spec()

        self.assertIsNotNone(result.assignment)
        # Non-empty string should still use from_code for expressions
        self.assertEqual(result.assignment.flavor, AssignmentFlavor.CODE)
        self.assertEqual(result.assignment.code, "some_value")


if __name__ == "__main__":
    unittest.main()
