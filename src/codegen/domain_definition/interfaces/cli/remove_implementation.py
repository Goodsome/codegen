"""
RemoveImplementation command - Remove an implementation from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_implementation import (
    RemoveImplementation,
    RemoveImplementationCommand,
    RemoveImplementationResult,
)


@inject
def _remove_implementation(
    cmd: RemoveImplementationCommand,
    use_case: RemoveImplementation = Provide[
        "domain_definition_container.remove_implementation"
    ],
) -> RemoveImplementationResult:
    return use_case.execute(cmd)


def remove_implementation(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Implementation name")],
) -> None:
    """
    Remove an implementation from a bounded context.

    Examples:
        $ codegen infrastructure remove-implementation Sales postgres
        $ codegen infrastructure remove-implementation Billing stripe
    """
    cmd = RemoveImplementationCommand(context_name=context_name, name=name)
    result = _remove_implementation(cmd)
    if result.success:
        typer.echo(f"Successfully removed implementation '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove implementation '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
