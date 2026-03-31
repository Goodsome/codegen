"""
RemoveMethod command - Remove a method from an element.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_method import (
    RemoveMethod,
    RemoveMethodCommand,
    RemoveMethodResult,
)
from codegen.domain_definition.domain.enums import ElementType, MethodKind


@inject
def _remove_method(
    cmd: RemoveMethodCommand,
    use_case: RemoveMethod = Provide["domain_definition_container.remove_method"],
) -> RemoveMethodResult:
    return use_case.execute(cmd)


def remove_method(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    element_type: Annotated[ElementType, typer.Argument(help="Element type")],
    method_kind: Annotated[MethodKind, typer.Argument(help="Method kind")],
    element_name: Annotated[str, typer.Argument(help="Element name")],
    name: Annotated[str, typer.Argument(help="Method name to remove")],
) -> None:
    """
    Remove a method from an element.

    Examples:
        $ codegen field remove-method sales entity behavior Order calculate_total
    """
    cmd = RemoveMethodCommand(
        context_name=context_name,
        element_type=element_type,
        method_kind=method_kind,
        element_name=element_name,
        name=name,
    )
    result = _remove_method(cmd)
    if result.success:
        typer.echo(f"Successfully removed {method_kind.value} '{name}'")
    else:
        typer.echo(f"Failed to remove {method_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
