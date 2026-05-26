import ast
from codegen.code_metadata.infrastructure.mappers.ast_module_to_component import AstModuleToComponent

def test_parse_assign_valid():
    mapper = AstModuleToComponent()
    code = """
Component = Annotated[
    ClassComponent | UnionComponent,
    Field(discriminator="kind"),
]
"""
    node = ast.parse(code).body[0]
    assert isinstance(node, ast.Assign)
    
    res = mapper.parse_assign(node, "Component")
    assert res is not None
    assert res.name == "Component"
    assert res.members == ["ClassComponent", "UnionComponent"]
    assert res.discriminator == "kind"

def test_parse_assign_invalid():
    mapper = AstModuleToComponent()
    
    # 1. 名字不匹配
    code1 = "Other = Annotated[ClassComponent | UnionComponent, Field(discriminator='kind')]"
    node1 = ast.parse(code1).body[0]
    assert mapper.parse_assign(node1, "Component") is None
    
    # 2. 没有 Field 或者是其他 annotation
    code2 = "Component = Annotated[ClassComponent | UnionComponent, SomeOther]"
    node2 = ast.parse(code2).body[0]
    assert mapper.parse_assign(node2, "Component") is None

    # 3. Field 里没有 discriminator
    code3 = "Component = Annotated[ClassComponent | UnionComponent, Field(description='hello')]"
    node3 = ast.parse(code3).body[0]
    assert mapper.parse_assign(node3, "Component") is None

    # 4. 不是 Annotated
    code4 = "Component = ClassComponent | UnionComponent"
    node4 = ast.parse(code4).body[0]
    assert mapper.parse_assign(node4, "Component") is None
