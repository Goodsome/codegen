
import pytest
from codegen.python_gen.infrastructure.adapters.ast_translator import AstTranslator
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.enums import AssignmentFlavor

class TestReproduceIssue:
    
    def test_reverse_function_with_complex_default(self):
        """Test parsing a function with a complex default value (expression)."""
        translator = AstTranslator()
        code = """
def foo(x: int = 1 + 1):
    pass
"""
        # This might crash or return incomplete spec
        spec = translator.parse_module(code, "test_mod")
        
        assert len(spec.functions) == 1
        func = spec.functions[0]
        assert func.name == "foo"
        assert len(func.parameters) == 1
        param = func.parameters[0]
        assert param.name == "x"
        # The assignment should be captured
        assert param.assignment is not None
        assert "1 + 1" in param.assignment.code

    def test_reverse_function_with_list_default(self):
        """Test parsing a function with a list default value."""
        translator = AstTranslator()
        code = """
def bar(items = []):
    pass
"""
        spec = translator.parse_module(code, "test_mod")
        func = spec.functions[0]
        param = func.parameters[0]
        assert param.assignment is not None
        assert "[]" in param.assignment.code

    def test_build_function_with_defaults(self):
        """Test building a function with defaults."""
        translator = AstTranslator()
        
        # Construct a spec that mimics what we expect from parsing
        assign = AssignmentSpec(flavor=AssignmentFlavor.CODE, code="1 + 1")
        param = VariableSpec.create(name="x", type_spec=TypeAnnotationSpec(name="int"), assignment=assign)
        
        func = FunctionSpec.create(
            name="foo",
            parameters=[param],
            return_annotation=TypeAnnotationSpec(name="None")
        )
        
        module = ModuleSpec.create(name="test_build", functions=[func])
        
        # This might fail if builder doesn't handle assignment correctly
        code = translator.render_module(module, [])
        
        # Format code to avoid whitespace issues
        import black
        formatted_code = black.format_str(code, mode=black.Mode())
        
        # Verification: we expect valid python code
        assert "def foo(x: int = 1 + 1) -> None:" in formatted_code
