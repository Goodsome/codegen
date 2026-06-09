from typing import Annotated, Literal
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.shared.domain.core import ValueObject


class ImportsEdgeProperties(ValueObject):
    kind: Literal[EdgeType.IMPORTS] = EdgeType.IMPORTS
    is_type_checking: bool

