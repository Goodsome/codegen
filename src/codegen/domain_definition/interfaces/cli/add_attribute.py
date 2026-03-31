"""
AddAttribute command - Add an attribute/dependency/input/output to an element.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_attribute import (
    AddAttribute,
    AddAttributeCommand,
    AddAttributeResult,
)
from codegen.domain_definition.domain.enums import AttributeKind, ElementType


@inject
def _add_attribute(
    cmd: AddAttributeCommand,
    use_case: AddAttribute = Provide["domain_definition_container.add_attribute"],
) -> AddAttributeResult:
    return use_case.execute(cmd)


def add_attribute(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    element_type: Annotated[ElementType, typer.Argument(help="Element type")],
    attribute_kind: Annotated[AttributeKind, typer.Argument(help="Attribute kind")],
    element_name: Annotated[str, typer.Argument(help="Element name")],
    name: Annotated[str, typer.Argument(help="Attribute name")],
    type: Annotated[str, typer.Argument(help="Attribute type")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
    default: Annotated[str | None, typer.Option("--default")] = None,
    optional: Annotated[bool, typer.Option("--optional")] = False,
) -> None:
    """
    Add an attribute, dependency, input, or output to an element.

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
    )
    result = _add_attribute(cmd)
    if result.success:
        typer.echo(f"Successfully added {attribute_kind.value} '{name}' to {element_type.value} '{element_name}'")
    else:
        typer.echo(f"Failed to add {attribute_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
