import ast
import pytest
from codegen.python_gen.domain.value_objects.enum_spec import EnumSpec
from codegen.python_gen.domain.value_objects.enum_member_spec import EnumMemberSpec


def test_enum_member_spec_parse_ast_assign():
    code = "A = 1"
    tree = ast.parse(code)
    node = tree.body[0]
    spec = EnumMemberSpec.parse_ast(node)
    assert spec.name == "A"
    assert spec.value == 1


def test_enum_member_spec_parse_ast_ann_assign():
    code = "A: int = 1"
    tree = ast.parse(code)
    node = tree.body[0]
    spec = EnumMemberSpec.parse_ast(node)
    assert spec.name == "A"
    assert spec.value == 1


def test_enum_spec_parse_ast():
    code = """
@decorator
class MyEnum(Enum):
    \"\"\"My Doc\"\"\"
    A = 1
    B = "hello"
    C: int = 3
    __private = 4
"""
    tree = ast.parse(code)
    node = tree.body[0]
    assert isinstance(node, ast.ClassDef)

    spec = EnumSpec.parse_ast(node)
    assert spec.name == "MyEnum"
    assert spec.description == "My Doc"
    assert spec.decorators == ["decorator"]
    assert spec.base_class == "Enum"
    assert len(spec.members) == 3
    assert spec.members[0].name == "A"
    assert spec.members[0].value == 1
    assert spec.members[1].name == "B"
    assert spec.members[1].value == "hello"
    assert spec.members[2].name == "C"
    assert spec.members[2].value == 3


def test_enum_spec_create():
    member = EnumMemberSpec.create(name="A", value=1)
    spec = EnumSpec.create(name="MyEnum", members=[member])
    assert spec.name == "MyEnum"
    assert len(spec.members) == 1
    assert spec.members[0].name == "A"
