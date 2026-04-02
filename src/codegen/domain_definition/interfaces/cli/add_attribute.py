import typer
from typing import Annotated
from dependency_injector.wiring import Provide, inject
from codegen.domain_definition.application.use_cases.add_attribute import (
    AddAttribute,
    AddAttributeCommand,
    AddAttributeResult,
)
from codegen.domain_definition.domain.enums import AttributeKind, ElementType
from codegen.shared.domain.enums import ContainerType


@inject
def _add_attribute(
    cmd: AddAttributeCommand,
    use_case: AddAttribute = Provide["domain_definition_container.add_attribute"],
) -> AddAttributeResult:
    return use_case.execute(cmd)


def add_attribute(
    context_name: Annotated[str, typer.Argument()],
    element_type: Annotated[ElementType, typer.Argument()],
    attribute_kind: Annotated[AttributeKind, typer.Argument()],
    element_name: Annotated[str, typer.Argument()],
    name: Annotated[str, typer.Argument()],
    type: Annotated[str, typer.Argument()],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
    default: Annotated[str | None, typer.Option("--default", "-d2")] = None,
    container: Annotated[
        ContainerType, typer.Option("--container", "-c")
    ] = ContainerType.NONE,
    optional: Annotated[bool, typer.Option("--optional", "-o")] = False,
    custom_type_string: Annotated[
        str | None, typer.Option("--custom-type-string", "-cts")
    ] = None,
) -> None:
    """Add an attribute, dependency, input, or output to an element.

    Examples:
        $ codegen field add sales entity attribute Order order_id string
        $ codegen field add sales entity attribute Order customer_id string --optional
        $ codegen field add sales use_case dependency CreateOrder repo Repository
    """
    cmd = AddAttributeCommand(
        context_name=context_name,
        element_type=element_type,
        attribute_kind=attribute_kind,
        element_name=element_name,
        name=name,
        type=type,
        description=description,
        default=default,
        optional=optional,
        container=container,
        custom_type_string=custom_type_string,
    )
    result = _add_attribute(cmd)
    if result.success:
        typer.echo(
            f"Successfully added {attribute_kind.value} '{name}' to {element_type.value} '{element_name}'"
        )
    else:
        typer.echo(f"Failed to add {attribute_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
