from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.enums import ElementType, MethodKind
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.rule_spec import RuleSpec
from codegen.shared.domain.enums import ContainerType
from codegen.shared.domain.value_objects.snake_string import SnakeString


class AddMethodCommand(BaseModel):
    """Command to add a method (behavior, operation, or private) to an element."""

    context_name: str
    element_type: ElementType
    method_kind: MethodKind
    element_name: str
    name: str
    description: str
    inputs: list[dict[str, Any]] = Field(default_factory=list)
    rules: list[dict[str, Any]] = Field(default_factory=list)
    output_type: str = Field(default="void")
    output_container: ContainerType = Field(default=ContainerType.NONE)
    output_optional: bool = Field(default=False)
    output_custom_type_string: str | None = Field(default=None)


class AddMethodResult(BaseModel):
    success: bool


@dataclass
class AddMethod:
    """Use case to add a method to an element."""

    storage: BlueprintStorage

    def execute(self, cmd: AddMethodCommand) -> AddMethodResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        # Build inputs from list of dicts
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

        # Build rules from list of dicts
        rules = [
            RuleSpec(
                name=SnakeString(rule["name"]),
                given=rule["given"],
                when=rule["when"],
                then=rule["then"],
            )
            for rule in cmd.rules
        ]

        # Build output
        output = MethodOutput(
            type=cmd.output_type,
            container=cmd.output_container,
            optional=cmd.output_optional,
            custom_type_string=cmd.output_custom_type_string,
        )

        method = MethodSpec(
            name=SnakeString(cmd.name),
            description=cmd.description,
            inputs=inputs,
            output=output,
            rules=rules,
        )

        match (cmd.element_type, cmd.method_kind):
            case (ElementType.AGGREGATE, MethodKind.BEHAVIOR):
                context.domain.get_aggregate(cmd.element_name).behaviors.add(method)
            case (ElementType.ENTITY, MethodKind.BEHAVIOR):
                context.domain.get_entity(cmd.element_name).behaviors.add(method)
            case (ElementType.VALUE_OBJECT, MethodKind.BEHAVIOR):
                context.domain.get_value_object(cmd.element_name).behaviors.add(method)
            case (ElementType.DOMAIN_SERVICE, MethodKind.OPERATION):
                context.domain.get_service(cmd.element_name).operations.add(method)
            case (ElementType.APP_SERVICE, MethodKind.OPERATION):
                context.application.get_service(cmd.element_name).operations.add(method)
            case (ElementType.DOMAIN_PORT, MethodKind.OPERATION):
                context.domain.get_port(cmd.element_name).operations.add(method)
            case (ElementType.APP_PORT, MethodKind.OPERATION):
                context.application.get_port(cmd.element_name).operations.add(method)
            case (ElementType.IMPLEMENTATION, MethodKind.PRIVATE):
                context.infrastructure.get_implementation(
                    cmd.element_name
                ).private_methods.add(method)
            case _:
                raise ValueError(
                    f"Unsupported combination: element_type='{cmd.element_type.value}', "
                    f"method_kind='{cmd.method_kind.value}'"
                )

        self.storage.save(blueprint)

        return AddMethodResult(success=True)
