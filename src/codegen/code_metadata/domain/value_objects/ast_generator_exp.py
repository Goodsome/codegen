from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_list_comp import AstComprehension


@dataclass
class AstGeneratorExp(AstExpr):
    """Represents an ast.GeneratorExp node."""

    elt: AstExpr
    generators: list[AstComprehension] = field(default_factory=list)
