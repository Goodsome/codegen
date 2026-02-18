import pytest
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.enums import AssignmentFlavor
from codegen.python_gen.domain.value_objects.literal_spec import LiteralSpec

class TestVariableSpecEnhancement:
    """Test using VariableSpec as a function parameter (ParameterSpec replacement)."""

    def test_create_variable_without_assignment(self):
        """Test creating a VariableSpec without an assignment (required parameter)."""
        # This is expected to fail before we modify VariableSpec to make assignment optional
        # But we write it as we want it to behave.
        var = VariableSpec.create(
            name="param_required",
            type_spec=TypeAnnotationSpec(name="int"),
            assignment=None
        )
        assert var.name == "param_required"
        assert var.type_spec.render() == "int"
        assert var.assignment is None

    def test_create_variable_with_assignment(self):
        """Test creating a VariableSpec with an assignment (parameter with default value)."""
        assignment = AssignmentSpec(
            flavor=AssignmentFlavor.LITERAL,
            literal=LiteralSpec(value=1)
        )
        var = VariableSpec.create(
            name="param_default",
            type_spec=TypeAnnotationSpec(name="int"),
            assignment=assignment
        )
        assert var.name == "param_default"
        assert var.type_spec.render() == "int"
        assert var.assignment == assignment
    
    def test_optional_flag_for_compatibility(self):
        """
        Check if we need an 'optional' property directly on VariableSpec 
        or if we rely on type_spec.is_optional()
        """
        # ParameterSpec had an 'optional' field: optional: bool = Field(default=False)
        # VariableSpec currently doesn't. 
        # When mapping, if we say "optional=True", usually it means the TYPE is Optional[T] 
        # OR the parameter has a default value of None.
        
        # This test ensures we can construct what we need.
        type_spec = TypeAnnotationSpec(name="str")
        var = VariableSpec.create(
            name="test",
            type_spec=type_spec,
            assignment=None
        )
        # We might not need an explicit 'optional' flag if we infer it from type or assignment.
        assert var.name == "test"
