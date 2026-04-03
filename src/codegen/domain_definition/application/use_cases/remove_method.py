from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.enums import ElementType, MethodKind
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.snake_string import SnakeString


class RemoveMethodCommand(BaseModel):
    """Command to remove a method (behavior, operation, or private) from an element."""

    context_name: str
    element_type: ElementType
    method_kind: MethodKind
    element_name: str
    name: str


class RemoveMethodResult(BaseModel):
    success: bool


@dataclass
class RemoveMethod:
    """Use case to remove a method from an element."""

    storage: BlueprintStorage

    def execute(self, cmd: RemoveMethodCommand) -> RemoveMethodResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        method_name = SnakeString(cmd.name)

        match (cmd.element_type, cmd.method_kind):
            case (ElementType.AGGREGATE, MethodKind.BEHAVIOR):
                context.domain.get_aggregate(cmd.element_name).behaviors.remove(
                    method_name
                )
            case (ElementType.ENTITY, MethodKind.BEHAVIOR):
                context.domain.get_entity(cmd.element_name).behaviors.remove(method_name)
            case (ElementType.VALUE_OBJECT, MethodKind.BEHAVIOR):
                context.domain.get_value_object(cmd.element_name).behaviors.remove(
                    method_name
                )
            case (ElementType.DOMAIN_SERVICE, MethodKind.OPERATION):
                context.domain.get_service(cmd.element_name).operations.remove(
                    method_name
                )
            case (ElementType.APP_SERVICE, MethodKind.OPERATION):
                context.application.get_service(cmd.element_name).operations.remove(
                    method_name
                )
            case (ElementType.DOMAIN_PORT, MethodKind.OPERATION):
                context.domain.get_port(cmd.element_name).operations.remove(method_name)
            case (ElementType.APP_PORT, MethodKind.OPERATION):
                context.application.get_port(cmd.element_name).operations.remove(
                    method_name
                )
            case (ElementType.IMPLEMENTATION, MethodKind.PRIVATE):
                context.infrastructure.get_implementation(
                    cmd.element_name
                ).private_methods.remove(method_name)
            case _:
                raise ValueError(
                    f"Unsupported combination: element_type='{cmd.element_type.value}', "
                    f"method_kind='{cmd.method_kind.value}'"
                )

        self.storage.save(blueprint)

        return RemoveMethodResult(success=True)
