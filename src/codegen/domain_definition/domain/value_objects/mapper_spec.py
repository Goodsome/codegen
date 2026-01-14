from codegen.domain_definition.domain.enums import MappingDirection
from codegen.shared.models import ValueObject


class MapperSpec(ValueObject):
    """Base class for value object mappers."""

    source: str
    target: str
    direction: MappingDirection
