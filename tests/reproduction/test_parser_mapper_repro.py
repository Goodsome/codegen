import ast
from codegen.python_gen.infrastructure.adapters.ast_parsers.function_parser import parse_parameter_from_assign
from codegen.python_gen.domain.enums import AssignmentFlavor
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.call_spec import CallSpec
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper

def test_parser_produces_call_flavor_for_field():
    code = "x: list[int] = Field(default_factory=list)"
    node = ast.parse(code).body[0] # AnnAssign
    
    # This calls the function_parser logic
    specs = parse_parameter_from_assign(node)
    
    assert len(specs) == 1
    spec = specs[0]
    
    assert spec.assignment is not None
    # Current behavior: flavor is CODE
    # Expected behavior: flavor is CALL
    
    # We assert the DESIRED behavior here to fail until fixed
    assert spec.assignment.flavor == AssignmentFlavor.CALL
    assert spec.assignment.call is not None
    assert spec.assignment.call.callee == "Field"
    assert "default_factory" in spec.assignment.call.kwargs

def test_mapper_handles_call_flavor():
    # This is the test we had before, ensuring mapper works if parser is fixed
    from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
    from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec
    
    mapper = AttributeMapper()
    
    # Construct a spec as if parser produced it correctly
    call_spec = CallSpec(
        callee="Field",
        args=[],
        kwargs={"default_factory": AssignmentSpec.from_code("list")}
    )
    assignment = AssignmentSpec(
        flavor=AssignmentFlavor.CALL,
        call=call_spec,
        code="Field(default_factory=list)"
    )
    
    var_spec = VariableSpec(
        name="my_list",
        type_spec=TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="int")]),
        assignment=assignment
    )
    
    attr = mapper.to_attribute(var_spec)
    
    assert attr.optional is True
    assert attr.default is None
