"""
UpdateImplementation command - Update an existing implementation in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_implementation import (
    UpdateImplementation,
    UpdateImplementationCommand,
    UpdateImplementationResult,
)


@inject
def _update_implementation(
    cmd: UpdateImplementationCommand,
    use_case: UpdateImplementation = Provide[
        "domain_definition_container.update_implementation"
    ],
) -> UpdateImplementationResult:
    return use_case.execute(cmd)


def update_implementation(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Implementation name")],
    implements: Annotated[str | None, typer.Option("--implements", "-i")] = None,
    technology: Annotated[str | None, typer.Option("--technology", "-t")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing implementation in a bounded context.

    Examples:
        $ codegen infrastructure update-implementation Sales postgres --technology "PostgreSQL 15"
        $ codegen infrastructure update-implementation Billing stripe --description "Updated Stripe gateway"
    """
    cmd = UpdateImplementationCommand(
        context_name=context_name,
        name=name,
        implements=implements,
        technology=technology,
        description=description,
    )
    result = _update_implementation(cmd)
    if result.success:
        typer.echo(f"Successfully updated implementation '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update implementation '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
