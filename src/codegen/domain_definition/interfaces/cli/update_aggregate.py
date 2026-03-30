"""
UpdateAggregate command - Update an existing aggregate in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_aggregate import (
    UpdateAggregate,
    UpdateAggregateCommand,
    UpdateAggregateResult,
)


@inject
def _update_aggregate(
    cmd: UpdateAggregateCommand,
    use_case: UpdateAggregate = Provide["domain_definition_container.update_aggregate"],
) -> UpdateAggregateResult:
    return use_case.execute(cmd)


def update_aggregate(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Aggregate name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing aggregate in a bounded context.
    """
    cmd = UpdateAggregateCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_aggregate(cmd)
    if result.success:
        typer.echo(f"Successfully updated aggregate '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update aggregate '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
