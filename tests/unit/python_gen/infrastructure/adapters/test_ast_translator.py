import pytest
from codegen.python_gen.infrastructure.adapters.ast_translator import AstTranslator
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec

class TestAstTranslatorBuilders:
    """Unit tests for Spec -> AST builders."""

    def test_render_simple_module(self):
        translator = AstTranslator()
        module_spec = ModuleSpec.create(name="test_mod")
        source_code = translator.render_module(module_spec, [])
        assert isinstance(source_code, str)
    
    def test_render_empty_module(self):
        """Test rendering an empty module (e.g. __init__.py)."""
        translator = AstTranslator()
        module_spec = ModuleSpec.create(name="empty")
        source_code = translator.render_module(module_spec, [])
        assert isinstance(source_code, str)
        # Empty module should generate empty string or just comments/whitespace
        assert source_code.strip() == "" or source_code.strip() == "#" 

    def test_render_module_with_imports(self):
        """Test rendering a module with imports."""
        translator = AstTranslator()
        module_spec = ModuleSpec.create(name="with_imports")
        imports = [
            ImportFromSpec.create(module="typing", names=["List", "Dict"])
        ]
        source_code = translator.render_module(module_spec, imports)
        # Since implementation is stubbed, this will likely fail or return None, but assertion is here.
        assert isinstance(source_code, str)
        assert "from typing import List, Dict" in source_code

    def test_render_module_with_classes_and_functions(self):
        translator = AstTranslator()
        
        # Create a spec
        func = FunctionSpec.create(
            name="hello",
            parameters=[
                ParameterSpec.create(name="name", annotation="str")
            ],
            return_annotation=TypeAnnotationSpec(name="str"),
            suite="return f'Hello {name}'"
        )
        cls = ClassSpec.create(
            name="Greeter",
            methods=[func]
        )
        module_spec = ModuleSpec.create(
            name="greetings",
            classes=[cls]
        )
        
        source_code = translator.render_module(module_spec, [])
        
        assert isinstance(source_code, str)
        assert "class Greeter" in source_code
        assert "def hello" in source_code
        assert "name: str" in source_code

class TestAstTranslatorParsers:
    """Unit tests for AST -> Spec parsers."""

    def test_parse_simple_class(self):
        translator = AstTranslator()
        code = """
class A:
    def method(self):
        pass
"""
        spec = translator.parse_module(code, "test_mod")
        
        assert isinstance(spec, ModuleSpec)
        assert spec.name == "test_mod"
        assert len(spec.classes) == 1
        assert spec.classes[0].name == "A"
        assert len(spec.classes[0].methods) == 1
        assert spec.classes[0].methods[0].name == "method"

    def test_parse_invalid_syntax(self):
        """Test parsing invalid Python code raises SyntaxError."""
        translator = AstTranslator()
        invalid_code = "class A def method():"  # Syntax error
        with pytest.raises(SyntaxError):
            translator.parse_module(invalid_code, "test_mod")

    def test_parse_unsupported_structure(self):
        """Test parsing unsupported structure raises ValueError."""
        # This test assumes the implementation will strictly validate unsupported constructs.
        # This might need adjustment if the parser is lenient.
        translator = AstTranslator()
        # Example: lambda expressions might not be supported mapping to Domain Specs directly if not wrapped
        # But lambda is valid python. A better example might be top-level expressions that are not supported.
        # The prompt suggested "unsupported structure".
        # Let's assume the Domain doesn't support global variables assigned to lambdas directly in ModuleSpec (it only has variables, classes, functions).
        # Actually ModuleSpec has `assignments` (VariableSpec), but maybe complex assignments are limited.
        # Let's stick to the prompt's example or similar intention.
        # Note: If invalid python, it raises SyntaxError.
        # If valid python but not representable in Spec (e.g. `if __name__ == "__main__": ...`), parser might ignore or raise.
        # Users prompt suggested: `code = "x = lambda y: y + 1"`
        code = "x = lambda y: y + 1"
        with pytest.raises(ValueError, match="unsupported"): # Expecting implementation to raise ValueError
            translator.parse_module(code, "test_mod")

class TestRoundTrip:
    """Round-trip tests: Spec -> Code -> Spec."""

    def test_round_trip_module(self):
        translator = AstTranslator()
        original_spec = ModuleSpec.create(
            name="rt_mod",
            classes=[ClassSpec.create(name="C")]
        )
        
        code = translator.render_module(original_spec, [])
        parsed_spec = translator.parse_module(code, "rt_mod")
        
        # Note: Inequality might happen if defaults differ (e.g. empty lists vs None), 
        # but ValueObjects should handle equality well if configured correctly.
        assert parsed_spec.name == original_spec.name
        assert len(parsed_spec.classes) == len(original_spec.classes)
        assert parsed_spec.classes[0].name == original_spec.classes[0].name
