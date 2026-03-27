"""Tests for SubscriptSpec and AssignmentSpec subscript support."""
import ast
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.enums import AssignmentFlavor
from codegen.python_gen.infrastructure.adapters.ast_parsers.assignment_parser import parse_assignment_value
from codegen.python_gen.infrastructure.adapters.ast_builders.assignment_builder import build_assignment_expr


class TestSubscriptSpec:
    """Test SubscriptSpec value object."""

    def test_subscript_spec_has_value_and_slice_fields(self):
        """SubscriptSpec should have value and slice fields of type AssignmentSpec."""
        from codegen.python_gen.domain.value_objects.subscript_spec import SubscriptSpec

        value_spec = AssignmentSpec.from_symbol("Provide")
        slice_spec = AssignmentSpec.from_literal("container.service")

        subscript_spec = SubscriptSpec(value=value_spec, slice=slice_spec)

        assert subscript_spec.value == value_spec
        assert subscript_spec.slice == slice_spec

    def test_subscript_spec_get_required_types_collects_from_value_and_slice(self):
        """SubscriptSpec.get_required_types() should collect types from both value and slice."""
        from codegen.python_gen.domain.value_objects.subscript_spec import SubscriptSpec

        value_spec = AssignmentSpec.from_symbol("Provide")
        slice_spec = AssignmentSpec.from_symbol("SomeType")

        subscript_spec = SubscriptSpec(value=value_spec, slice=slice_spec)

        required_types = subscript_spec.get_required_types()
        assert required_types == {"Provide", "SomeType"}


class TestAssignmentSpecFromSubscript:
    """Test AssignmentSpec.from_subscript() factory method."""

    def test_from_subscript_creates_subscript_flavor(self):
        """from_subscript should create AssignmentSpec with SUBSCRIPT flavor."""
        value_spec = AssignmentSpec.from_symbol("Provide")
        slice_spec = AssignmentSpec.from_code("container.service")

        spec = AssignmentSpec.from_subscript(value_spec, slice_spec)

        assert spec.flavor == AssignmentFlavor.SUBSCRIPT
        assert spec.subscript is not None
        assert spec.subscript.value == value_spec
        assert spec.subscript.slice == slice_spec

    def test_from_subscript_nested(self):
        """from_subscript should handle nested subscripts like a[b[c]]."""
        inner_value = AssignmentSpec.from_symbol("a")
        inner_slice = AssignmentSpec.from_symbol("b")
        inner_subscript = AssignmentSpec.from_subscript(inner_value, inner_slice)

        outer_slice = AssignmentSpec.from_symbol("c")
        outer_spec = AssignmentSpec.from_subscript(inner_subscript, outer_slice)

        assert outer_spec.flavor == AssignmentFlavor.SUBSCRIPT
        assert outer_spec.subscript.value.flavor == AssignmentFlavor.SUBSCRIPT


class TestAssignmentSpecGetRequiredTypesWithSubscript:
    """Test get_required_types() collects types from subscript.value only."""

    def test_get_required_types_from_subscript_value_only(self):
        """get_required_types should collect types from subscript.value, NOT subscript.slice."""
        # Provide["container.service"] - only "Provide" should be collected
        value_spec = AssignmentSpec.from_symbol("Provide")
        slice_spec = AssignmentSpec.from_code("container.service")

        spec = AssignmentSpec.from_subscript(value_spec, slice_spec)

        required_types = spec.get_required_types()
        assert required_types == {"Provide"}
        assert "container.service" not in required_types

    def test_get_required_types_nested_subscript(self):
        """Nested subscript: a[b[c]] should collect types from all subscript.value and subscript.slice chains."""
        inner_value = AssignmentSpec.from_symbol("Inner")
        inner_slice = AssignmentSpec.from_symbol("inner_key")
        inner_subscript = AssignmentSpec.from_subscript(inner_value, inner_slice)

        outer_slice = AssignmentSpec.from_symbol("outer_key")
        outer_spec = AssignmentSpec.from_subscript(inner_subscript, outer_slice)

        # Collects from all subscript.value and subscript.slice
        required_types = outer_spec.get_required_types()
        assert "Inner" in required_types
        assert "inner_key" in required_types
        assert "outer_key" in required_types


class TestAssignmentParserSubscript:
    """Test assignment_parser handles ast.Subscript nodes."""

    def test_parse_provide_subscript(self):
        """Parse Provide["container.service"] into SUBSCRIPT flavor."""
        code = 'Provide["container.service"]'
        tree = ast.parse(code, mode='eval')
        spec = parse_assignment_value(tree.body)

        assert spec.flavor == AssignmentFlavor.SUBSCRIPT
        assert spec.subscript is not None
        # value should be a symbol "Provide"
        assert spec.subscript.value.flavor == AssignmentFlavor.SYMBOL
        assert spec.subscript.value.reference.name == "Provide"
        # slice should be LITERAL (string literal is ast.Constant)
        assert spec.subscript.slice.flavor == AssignmentFlavor.LITERAL
        assert spec.subscript.slice.literal.value == "container.service"

    def test_parse_nested_subscript(self):
        """Parse a[b[c]] into nested SUBSCRIPT flavor."""
        code = "a[b[c]]"
        tree = ast.parse(code, mode='eval')
        spec = parse_assignment_value(tree.body)

        assert spec.flavor == AssignmentFlavor.SUBSCRIPT
        # value is "a" (SYMBOL), slice is "b[c]" (SUBSCRIPT)
        assert spec.subscript.value.flavor == AssignmentFlavor.SYMBOL
        assert spec.subscript.value.reference.name == "a"
        assert spec.subscript.slice.flavor == AssignmentFlavor.SUBSCRIPT


class TestAssignmentBuilderSubscript:
    """Test assignment_builder builds ast.Subscript from AssignmentSpec."""

    def test_build_subscript_spec(self):
        """Build ast.Subscript from AssignmentSpec with SUBSCRIPT flavor."""
        value_spec = AssignmentSpec.from_symbol("Provide")
        slice_spec = AssignmentSpec.from_code("container.service")
        spec = AssignmentSpec.from_subscript(value_spec, slice_spec)

        node = build_assignment_expr(spec)

        assert isinstance(node, ast.Subscript)
        assert isinstance(node.value, ast.Name)
        assert node.value.id == "Provide"
