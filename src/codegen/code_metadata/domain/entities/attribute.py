from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.entity import Entity


class Attribute(Entity):

    id: AttributeId
    name: str
    description: str
    type: TypeDef
    