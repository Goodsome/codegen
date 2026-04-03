from dataclasses import dataclass
from typing import Any, Self
from pydantic import BaseModel, Field
from codegen.domain_definition.domain.enums import AttributeKind, ElementType
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.domain.enums import ContainerType
from codegen.shared.domain.value_objects.snake_string import SnakeString


class AddAttributeCommand(BaseModel):
    context_name: str
    element_type: ElementType
    attribute_kind: AttributeKind
    element_name: str
    name: str
    type: str
    description: str | None = Field(default=None)
    default: Any | None = Field(default=None)
    container: ContainerType = Field(default=ContainerType.NONE)
    optional: bool = Field(default=False)
    custom_type_string: str | None = Field(default=None)


class AddAttributeResult(BaseModel):
    success: bool


@dataclass
class AddAttribute:
    """Use case to add an attribute, dependency, input, or output to an element."""

    storage: BlueprintStorage

    def execute(self: Self, cmd: AddAttributeCommand) -> AddAttributeResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")
        context = blueprint.get_context(cmd.context_name)
        attribute = AttributeSpec(
            name=SnakeString(cmd.name),
            type=cmd.type,
            description=cmd.description,
            default=cmd.default,
            container=cmd.container,
            optional=cmd.optional,
            custom_type_string=cmd.custom_type_string,
        )
        match (cmd.element_type, cmd.attribute_kind):
            case [ElementType.AGGREGATE, AttributeKind.ATTRIBUTE]:
                context.domain.get_aggregate(cmd.element_name).attributes.add(attribute)
            case [ElementType.ENTITY, AttributeKind.ATTRIBUTE]:
                context.domain.get_entity(cmd.element_name).attributes.add(attribute)
            case [ElementType.VALUE_OBJECT, AttributeKind.ATTRIBUTE]:
                context.domain.get_value_object(cmd.element_name).attributes.add(
                    attribute
                )
            case [ElementType.DOMAIN_SERVICE, AttributeKind.DEPENDENCY]:
                context.domain.get_service(cmd.element_name).dependencies.add(attribute)
            case [ElementType.APP_SERVICE, AttributeKind.DEPENDENCY]:
                context.application.get_service(cmd.element_name).dependencies.add(
                    attribute
                )
            case [ElementType.USE_CASE, AttributeKind.DEPENDENCY]:
                context.application.get_use_case(cmd.element_name).add_dependency(
                    attribute
                )
            case [ElementType.USE_CASE, AttributeKind.INPUT]:
                context.application.get_use_case(cmd.element_name).add_input(attribute)
            case [ElementType.USE_CASE, AttributeKind.OUTPUT]:
                context.application.get_use_case(cmd.element_name).add_output(attribute)
            case [ElementType.IMPLEMENTATION, AttributeKind.ATTRIBUTE]:
                context.infrastructure.get_implementation(
                    cmd.element_name
                ).attributes.add(attribute)
            case _:
                raise ValueError(
                    f"Unsupported combination: element_type='{cmd.element_type.value}', attribute_kind='{cmd.attribute_kind.value}'"
                )
        self.storage.save(blueprint)
        return AddAttributeResult(success=True)
