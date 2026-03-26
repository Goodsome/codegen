
import ast
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.enums import AssignmentFlavor


def build_assignment_expr(assignment: AssignmentSpec) -> ast.expr:
    """Builds an AST expression from an AssignmentSpec."""
    if not assignment:
        return ast.Constant(value=None)

    if assignment.code:
        try:
            return ast.parse(assignment.code, mode='eval').body
        except SyntaxError:
            pass

    if assignment.reference:
        try:
            return ast.parse(assignment.reference.name, mode='eval').body
        except SyntaxError:
            pass

    if assignment.literal:
        return ast.Constant(value=assignment.literal.value)

    if assignment.flavor == AssignmentFlavor.CALL and assignment.call:
        args = [build_assignment_expr(arg) for arg in assignment.call.args]
        keywords = [
            ast.keyword(arg=k, value=build_assignment_expr(v))
            for k, v in assignment.call.kwargs.items()
        ]

        # Determine func node (Name or Attribute)
        try:
            func_node = ast.parse(assignment.call.callee, mode='eval').body
        except SyntaxError:
            func_node = ast.Name(id=assignment.call.callee, ctx=ast.Load())

        return ast.Call(func=func_node, args=args, keywords=keywords)

    return ast.Constant(value=None)
