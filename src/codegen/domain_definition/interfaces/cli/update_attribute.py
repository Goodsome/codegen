"""
UpdateAttribute command - Update an attribute/dependency/input/output of an element.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_attribute import (
    UpdateAttribute,
    UpdateAttributeCommand,
    UpdateAttributeResult,
)
from codegen.domain_definition.domain.enums import AttributeKind, ElementType


@inject
def _update_attribute(
    cmd: UpdateAttributeCommand,
    use_case: UpdateAttribute = Provide["domain_definition_container.update_attribute"],
) -> UpdateAttributeResult:
    return use_case.execute(cmd)


def update_attribute(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    element_type: Annotated[ElementType, typer.Argument(help="Element type")],
    attribute_kind: Annotated[AttributeKind, typer.Argument(help="Attribute kind")],
    element_name: Annotated[str, typer.Argument(help="Element name")],
    name: Annotated[str, typer.Argument(help="Attribute name to update")],
    type: Annotated[str | None, typer.Option("--type", "-t")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
    default: Annotated[str | None, typer.Option("--default")] = None,
    optional: Annotated[bool | None, typer.Option("--optional")] = None,
) -> None:
    """
    Update an attribute, dependency, input, or output of an element.

    Examples:
        $ codegen field update sales entity attribute Order order_id --type string --optional
    """
    cmd = UpdateAttributeCommand(
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
    result = _update_attribute(cmd)
    if result.success:
        typer.echo(f"Successfully updated {attribute_kind.value} '{name}'")
    else:
        typer.echo(f"Failed to update {attribute_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
