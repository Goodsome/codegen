from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.enums import AttributeKind, ElementType
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.snake_string import SnakeString


class RemoveAttributeCommand(BaseModel):
    """Command to remove an attribute, dependency, input, or output from an element."""

    context_name: str
    element_type: ElementType
    attribute_kind: AttributeKind
    element_name: str
    name: str


class RemoveAttributeResult(BaseModel):
    success: bool


@dataclass
class RemoveAttribute:
    """Use case to remove an attribute, dependency, input, or output from an element."""

    storage: BlueprintStorage

    def execute(self, cmd: RemoveAttributeCommand) -> RemoveAttributeResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        attr_name = SnakeString(cmd.name)

        match (cmd.element_type, cmd.attribute_kind):
            case (ElementType.AGGREGATE, AttributeKind.ATTRIBUTE):
                context.domain.get_aggregate(cmd.element_name).attributes.remove(attr_name)
            case (ElementType.ENTITY, AttributeKind.ATTRIBUTE):
                context.domain.get_entity(cmd.element_name).attributes.remove(attr_name)
            case (ElementType.VALUE_OBJECT, AttributeKind.ATTRIBUTE):
                context.domain.get_value_object(cmd.element_name).attributes.remove(attr_name)
            case (ElementType.DOMAIN_EVENT, AttributeKind.ATTRIBUTE):
                context.domain.get_domain_event(cmd.element_name).attributes.remove(attr_name)
            case (ElementType.DOMAIN_EXCEPTION, AttributeKind.ATTRIBUTE):
                context.domain.get_domain_exception(cmd.element_name).attributes.remove(attr_name)
            case (ElementType.DOMAIN_SERVICE, AttributeKind.DEPENDENCY):
                context.domain.get_service(cmd.element_name).dependencies.remove(attr_name)
            case (ElementType.APP_SERVICE, AttributeKind.DEPENDENCY):
                context.application.get_service(cmd.element_name).dependencies.remove(attr_name)
            case (ElementType.USE_CASE, AttributeKind.DEPENDENCY):
                context.application.get_use_case(cmd.element_name).dependencies.remove(attr_name)
            case (ElementType.USE_CASE, AttributeKind.INPUT):
                context.application.get_use_case(cmd.element_name).inputs.remove(attr_name)
            case (ElementType.USE_CASE, AttributeKind.OUTPUT):
                context.application.get_use_case(cmd.element_name).outputs.remove(attr_name)
            case (ElementType.IMPLEMENTATION, AttributeKind.ATTRIBUTE):
                context.infrastructure.get_implementation(cmd.element_name).attributes.remove(attr_name)
            case _:
                raise ValueError(
                    f"Unsupported combination: element_type='{cmd.element_type.value}', "
                    f"attribute_kind='{cmd.attribute_kind.value}'"
                )

        self.storage.save(blueprint)

        return RemoveAttributeResult(success=True)
