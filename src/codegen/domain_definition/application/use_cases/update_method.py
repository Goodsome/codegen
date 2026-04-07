from dataclasses import dataclass
from typing import Any, Self
from pydantic import BaseModel, Field
from codegen.domain_definition.domain.enums import ElementType, MethodKind
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.rule_spec import RuleSpec
from codegen.shared.domain.enums import ContainerType
from codegen.shared.domain.value_objects.snake_string import SnakeString


class UpdateMethodCommand(BaseModel):
    context_name: str
    element_type: ElementType
    method_kind: MethodKind
    element_name: str
    name: str
    description: str
    output_type: str
    inputs: list[dict[str, Any]] | None = Field(default=None)
    rules: list[dict[str, Any]] | None = Field(default=None)
    output_container: ContainerType = Field(default=ContainerType.NONE)
    output_optional: bool = Field(default=False)
    output_custom_type_string: str | None = Field(default=None)


class UpdateMethodResult(BaseModel):
    success: bool


@dataclass
class UpdateMethod:
    """Use case to update a method of an element."""

    storage: BlueprintStorage

    def execute(self: Self, cmd: UpdateMethodCommand) -> UpdateMethodResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")
        context = blueprint.get_context(cmd.context_name)
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

        rules = None
        if cmd.rules is not None:
            rules = [
                RuleSpec(
                    name=SnakeString(rule["name"]),
                    given=rule["given"],
                    when=rule["when"],
                    then=rule["then"],
                )
                for rule in cmd.rules
            ]

        output = None
        if any(
            [
                cmd.output_type is not None,
                cmd.output_container is not None,
                cmd.output_optional is not None,
                cmd.output_custom_type_string is not None,
            ]
        ):
            output = MethodOutput(
                type=cmd.output_type or "void",
                container=cmd.output_container or ContainerType.NONE,
                optional=(
                    cmd.output_optional if cmd.output_optional is not None else False
                ),
                custom_type_string=cmd.output_custom_type_string,
            )
        if output is None:
            raise ValueError("Output fields must be provided")
        method = MethodSpec(
            name=SnakeString(cmd.name),
            description=cmd.description,
            inputs=inputs,
            output=output,
            rules=rules or [],
        )
        match (cmd.element_type, cmd.method_kind):
            case [ElementType.AGGREGATE, MethodKind.BEHAVIOR]:
                context.domain.get_aggregate(cmd.element_name).behaviors.update(method)
            case [ElementType.ENTITY, MethodKind.BEHAVIOR]:
                context.domain.get_entity(cmd.element_name).behaviors.update(method)
            case [ElementType.VALUE_OBJECT, MethodKind.BEHAVIOR]:
                context.domain.get_value_object(cmd.element_name).behaviors.update(
                    method
                )
            case [ElementType.DOMAIN_SERVICE, MethodKind.OPERATION]:
                context.domain.get_service(cmd.element_name).operations.update(method)
            case [ElementType.APP_SERVICE, MethodKind.OPERATION]:
                context.application.get_service(cmd.element_name).operations.update(
                    method
                )
            case [ElementType.DOMAIN_PORT, MethodKind.OPERATION]:
                context.domain.get_port(cmd.element_name).operations.update(method)
            case [ElementType.APP_PORT, MethodKind.OPERATION]:
                context.application.get_port(cmd.element_name).operations.update(method)
            case [ElementType.IMPLEMENTATION, MethodKind.PRIVATE]:
                context.infrastructure.get_implementation(
                    cmd.element_name
                ).private_methods.update(method)
            case _:
                raise ValueError(
                    f"Unsupported combination: element_type='{cmd.element_type.value}', method_kind='{cmd.method_kind.value}'"
                )
        self.storage.save(blueprint)
        return UpdateMethodResult(success=True)
