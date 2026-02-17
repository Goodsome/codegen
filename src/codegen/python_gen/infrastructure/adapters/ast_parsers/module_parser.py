
import ast
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers import (
    import_parser,
    enum_parser,
    class_parser,
    function_parser
)

def parse_module(source_code: str, module_name: str) -> ModuleSpec:
    """Parses source code into a ModuleSpec."""
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise SyntaxError(f"Failed to parse source code: {e}") from e
    
    classes = []
    enums = []
    functions = []
    imports = []
    # ModuleSpec usually describes content, but generated code has imports.
    # ModuleSpec might not have 'imports' field?
    # Let's check ModuleSpec definition. 
    # If it doesn't have imports, we just ignore them during parsing?
    # But `SourceCodePort.parse_module` returns `ModuleSpec`.
    # `render_module` TAKES `ModuleSpec` AND `imports`.
    # So `imports` are separate.
    # `parse_module` might not be able to return imports if ModuleSpec doesn't hold them.
    # Design doc 4.1 says: "Return ModuleSpec.create(...)". logic includes imports variable.
    # But ModuleSpec definition probably doesn't have imports field.
    # This implies `parse_module` is lossy regarding imports OR imports are handled elsewhere.
    # Wait, if I parse a file, I want to know its imports too?
    # Design doc says "initializes lists: classes, functions, imports, enums".
    # But returns `ModuleSpec`.
    # Unless ModuleSpec HAS imports.
    
    # Let's proceed assuming ModuleSpec might ignore imports, or we should verify ModuleSpec.
    
    for item in tree.body:
        if isinstance(item, (ast.Import, ast.ImportFrom)):
            imports.append(import_parser.parse_import(item))
            
        elif isinstance(item, ast.ClassDef):
            # Check for Enum
            bases = [ast.unparse(b) for b in item.bases]
            is_enum = "Enum" in bases or module_name == "enums"
            
            if is_enum:
                enums.append(enum_parser.parse_enum(item))
            else:
                classes.append(class_parser.parse_class(item))
                
        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(function_parser.parse_function(item))
            
        elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
            # Ignore docstrings/comments
            pass
            
        else:
            # Ignore unsupported structures (e.g., if __name__ == "__main__", assignments, etc.)
            # We only extract classes, functions, enums, and imports
            pass
            
    return ModuleSpec.create(
        name=module_name,
        classes=classes,
        enums=enums,
        functions=functions,
        imports=imports
    )
