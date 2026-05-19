from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.domain_exception import DomainException


class AttributeNotFound(DomainException):
    def __init__(
        self,
        component_id: ComponentId,
        attribute_id: AttributeId | None = None,
        attribute_name: str | None = None,
    ) -> None:
        attr_info = "unknown"
        if attribute_id:
            attr_info = str(attribute_id)
        elif attribute_name:
            attr_info = attribute_name
        message = f"Attribute not found: Attribute `{attr_info}`, component_id={component_id}"
        super().__init__(message)
