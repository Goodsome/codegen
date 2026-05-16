
import ast
from pathlib import Path
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers import (
    import_parser,
    enum_parser,
    class_parser,
    function_parser
)
from codegen.python_gen.domain.value_objects.module_assignment_spec import ModuleAssignmentSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec

def parse_module(
    source_code: str,
    module_name: str,
    path: Path | None = None,
) -> ModuleSpec:
    """Parses source code into a ModuleSpec."""
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise SyntaxError(f"Failed to parse `{module_name}`, source code: {e}") from e
    
    classes = []
    enums = []
    functions = []
    imports = []
    assignments = []
    extra_code = []
    
    for item in tree.body:
        # 1. Imports
        if isinstance(item, (ast.Import, ast.ImportFrom)):
            imports.append(import_parser.parse_import(item))
            continue
            
        # 2. If Block (TYPE_CHECKING only, others fallback)
        if isinstance(item, ast.If):
            is_type_checking = (
                (isinstance(item.test, ast.Name) and item.test.id == "TYPE_CHECKING") or
                (isinstance(item.test, ast.Attribute) and item.test.attr == "TYPE_CHECKING")
            )
            if is_type_checking:
                for sub_item in item.body:
                    if isinstance(sub_item, (ast.Import, ast.ImportFrom)):
                        imp = import_parser.parse_import(sub_item)
                        imp = imp.model_copy(update={'type_checking': True})
                        imports.append(imp)
                continue

        # 3. Class / Enum
        if isinstance(item, ast.ClassDef):
            bases = [ast.unparse(b) for b in item.bases]
            is_enum = "Enum" in bases or module_name == "enums"
            if is_enum:
                enums.append(enum_parser.parse_enum(item))
            else:
                classes.append(class_parser.parse_class(item))
            continue
            
        # 4. Functions
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(function_parser.parse_function(item))
            continue
            
        # 5. Docstrings / Comments (Ignore)
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
            continue

        # 6. Assignments (Simple only, complex fallback)
        if isinstance(item, ast.Assign):
            if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                name = item.targets[0].id
                value = ast.unparse(item.value)
                assignments.append(ModuleAssignmentSpec.create(name=name, value=value))
                continue

        if isinstance(item, ast.AnnAssign):
            if isinstance(item.target, ast.Name):
                name = item.target.id
                value = ast.unparse(item.value) if item.value else ""
                annotation = ast.unparse(item.annotation)
                assignments.append(ModuleAssignmentSpec.create(name=name, value=value, type_annotation=annotation))
                continue
            
        # 7. Fallback: Raw Code
        # This handles 'if __name__ == "__main__"', complex assignments, and any other unsupported nodes.
        code = ast.unparse(item)
        extra_code.append(RawCodeSpec.create(code=code))
            
    return ModuleSpec.create(
        name=module_name,
        classes=classes,
        enums=enums,
        functions=functions,
        imports=imports,
        assignments=assignments,
        extra_code=extra_code,
        path=path,
    )
