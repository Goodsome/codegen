from dataclasses import dataclass
from typing import Any, Self
from pydantic import BaseModel, Field
from codegen.domain_definition.domain.enums import AttributeKind, ElementType
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.domain.enums import ContainerType
from codegen.shared.domain.value_objects.snake_string import SnakeString


class UpdateAttributeCommand(BaseModel):
    context_name: str
    element_type: ElementType
    attribute_kind: AttributeKind
    element_name: str
    name: str
    type: str | None = Field(default=None)
    description: str | None = Field(default=None)
    default: Any | None = Field(default=None)
    container: ContainerType | None = Field(default=None)
    optional: bool | None = Field(default=None)
    custom_type_string: str | None = Field(default=None)


class UpdateAttributeResult(BaseModel):
    success: bool


@dataclass
class UpdateAttribute:
    """Use case to update an attribute, dependency, input, or output of an element."""

    storage: BlueprintStorage

    def execute(self: Self, cmd: UpdateAttributeCommand) -> UpdateAttributeResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")
        context = blueprint.get_context(cmd.context_name)
        updated = AttributeSpec(
            name=SnakeString(cmd.name),
            type=cmd.type or "string",
            description=cmd.description,
            default=cmd.default,
            container=cmd.container or ContainerType.NONE,
            optional=cmd.optional if cmd.optional is not None else False,
            custom_type_string=cmd.custom_type_string,
        )
        match (cmd.element_type, cmd.attribute_kind):
            case [ElementType.AGGREGATE, AttributeKind.ATTRIBUTE]:
                context.domain.get_aggregate(cmd.element_name).attributes.update(updated)
            case [ElementType.ENTITY, AttributeKind.ATTRIBUTE]:
                context.domain.get_entity(cmd.element_name).attributes.update(updated)
            case [ElementType.VALUE_OBJECT, AttributeKind.ATTRIBUTE]:
                context.domain.get_value_object(cmd.element_name).attributes.update(
                    updated
                )
            case [ElementType.DOMAIN_SERVICE, AttributeKind.DEPENDENCY]:
                context.domain.get_service(cmd.element_name).dependencies.update(updated)
            case [ElementType.APP_SERVICE, AttributeKind.DEPENDENCY]:
                context.application.get_service(cmd.element_name).dependencies.update(
                    updated
                )
            case [ElementType.USE_CASE, AttributeKind.DEPENDENCY]:
                context.application.get_use_case(cmd.element_name).dependencies.update(
                    updated
                )
            case [ElementType.USE_CASE, AttributeKind.INPUT]:
                context.application.get_use_case(cmd.element_name).inputs.update(updated)
            case [ElementType.USE_CASE, AttributeKind.OUTPUT]:
                context.application.get_use_case(cmd.element_name).outputs.update(
                    updated
                )
            case [ElementType.IMPLEMENTATION, AttributeKind.ATTRIBUTE]:
                context.infrastructure.get_implementation(
                    cmd.element_name
                ).attributes.update(updated)
            case _:
                raise ValueError(
                    f"Unsupported combination: element_type='{cmd.element_type.value}', attribute_kind='{cmd.attribute_kind.value}'"
                )
        self.storage.save(blueprint)
        return UpdateAttributeResult(success=True)
