from codegen.bootstrap import Container
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec


def test_parse_code(default_container: Container):
    source_code = """
from pydantic import Field
from codegen.shared.models import ValueObject


class Attribute(ValueObject):
    \"\"\"Standard specification for a class attribute.\"\"\"

    name: str
    type: str
    description: str = Field(default_factory=str)
    optional: bool = Field(default_factory=bool)

    """

    module_spec = ModuleSpec.parse_code(source_code, "test")
    translator = default_container.python_syntax_translator_provider()
    content = translator.to_code(
        module_spec,
        module_spec.imports,
    )
