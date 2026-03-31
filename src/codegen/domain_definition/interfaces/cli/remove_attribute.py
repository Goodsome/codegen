"""
RemoveAttribute command - Remove an attribute/dependency/input/output from an element.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_attribute import (
    RemoveAttribute,
    RemoveAttributeCommand,
    RemoveAttributeResult,
)
from codegen.domain_definition.domain.enums import AttributeKind, ElementType


@inject
def _remove_attribute(
    cmd: RemoveAttributeCommand,
    use_case: RemoveAttribute = Provide["domain_definition_container.remove_attribute"],
) -> RemoveAttributeResult:
    return use_case.execute(cmd)


def remove_attribute(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    element_type: Annotated[ElementType, typer.Argument(help="Element type")],
    attribute_kind: Annotated[AttributeKind, typer.Argument(help="Attribute kind")],
    element_name: Annotated[str, typer.Argument(help="Element name")],
    name: Annotated[str, typer.Argument(help="Attribute name to remove")],
) -> None:
    """
    Remove an attribute, dependency, input, or output from an element.

    Examples:
        $ codegen field remove sales entity attribute Order order_id
    """
    cmd = RemoveAttributeCommand(
        context_name=context_name,
        element_type=element_type,
        attribute_kind=attribute_kind,
        element_name=element_name,
        name=name,
    )
    result = _remove_attribute(cmd)
    if result.success:
        typer.echo(f"Successfully removed {attribute_kind.value} '{name}'")
    else:
        typer.echo(f"Failed to remove {attribute_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
