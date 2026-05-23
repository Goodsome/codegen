
from codegen.shared.domain.core import ValueObject


class ReferenceSource(ValueObject):
    context: str
    components: list[str]