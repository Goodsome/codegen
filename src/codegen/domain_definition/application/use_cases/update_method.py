from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.enums import ElementType, MethodKind
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.shared.domain.enums import ContainerType
from codegen.shared.domain.value_objects.snake_string import SnakeString


class UpdateMethodCommand(BaseModel):
    """Command to update a method (behavior, operation, or private) of an element."""

    context_name: str
    element_type: ElementType
    method_kind: MethodKind
    element_name: str
    name: str
    description: str | None = Field(default=None)
    inputs: list[dict[str, Any]] | None = Field(default=None)
    # output fields (expanded from MethodOutput/TypeDefinition)
    output_type: str | None = Field(default=None)
    output_container: ContainerType | None = Field(default=None)
    output_optional: bool | None = Field(default=None)
    output_custom_type_string: str | None = Field(default=None)


class UpdateMethodResult(BaseModel):
    success: bool


@dataclass
class UpdateMethod:
    """Use case to update a method of an element."""

    storage: BlueprintStorage

    def execute(self, cmd: UpdateMethodCommand) -> UpdateMethodResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        # Build inputs from list of dicts if provided
        inputs = None
        if cmd.inputs is not None:
            inputs = [
                AttributeSpec(
                    name=SnakeString(inp["name"]),
                    type=inp.get("type", "string"),
                    description=inp.get("description"),
                    default=inp.get("default"),
                    container=inp.get("container", ContainerType.NONE),
                    optional=inp.get("optional", False),
                    custom_type_string=inp.get("custom_type_string"),
                )
                for inp in cmd.inputs
            ]

        # Build output only if at least one output field is provided
        output = None
        if any([
            cmd.output_type is not None,
            cmd.output_container is not None,
            cmd.output_optional is not None,
            cmd.output_custom_type_string is not None,
        ]):
            output = MethodOutput(
                type=cmd.output_type or "void",
                container=cmd.output_container or ContainerType.NONE,
                optional=cmd.output_optional if cmd.output_optional is not None else False,
                custom_type_string=cmd.output_custom_type_string,
            )

        method = MethodSpec(
            name=SnakeString(cmd.name),
            description=cmd.description,
            inputs=inputs,
            output=output,
        )

        match (cmd.element_type, cmd.method_kind):
            case (ElementType.AGGREGATE, MethodKind.BEHAVIOR):
                context.domain.get_aggregate(cmd.element_name).update_behavior(method)
            case (ElementType.ENTITY, MethodKind.BEHAVIOR):
                context.domain.get_entity(cmd.element_name).update_behavior(method)
            case (ElementType.VALUE_OBJECT, MethodKind.BEHAVIOR):
                context.domain.get_value_object(cmd.element_name).update_behavior(method)
            case (ElementType.DOMAIN_SERVICE, MethodKind.OPERATION):
                context.domain.get_service(cmd.element_name).update_operation(method)
            case (ElementType.APP_SERVICE, MethodKind.OPERATION):
                context.application.get_service(cmd.element_name).update_operation(method)
            case (ElementType.DOMAIN_PORT, MethodKind.OPERATION):
                context.domain.get_port(cmd.element_name).update_operation(method)
            case (ElementType.APP_PORT, MethodKind.OPERATION):
                context.application.get_port(cmd.element_name).update_operation(method)
            case (ElementType.IMPLEMENTATION, MethodKind.PRIVATE):
                context.infrastructure.get_implementation(cmd.element_name).update_private_method(method)
            case _:
                raise ValueError(
                    f"Unsupported combination: element_type='{cmd.element_type.value}', "
                    f"method_kind='{cmd.method_kind.value}'"
                )

        self.storage.save(blueprint)

        return UpdateMethodResult(success=True)
