"""
RemoveAggregate command - Remove an aggregate from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_aggregate import (
    RemoveAggregate,
    RemoveAggregateCommand,
    RemoveAggregateResult,
)


@inject
def _remove_aggregate(
    cmd: RemoveAggregateCommand,
    use_case: RemoveAggregate = Provide["domain_definition_container.remove_aggregate"],
) -> RemoveAggregateResult:
    return use_case.execute(cmd)


def remove_aggregate(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Aggregate name")],
) -> None:
    """
    Remove an aggregate from a bounded context.
    """
    cmd = RemoveAggregateCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_aggregate(cmd)
    if result.success:
        typer.echo(f"Successfully removed aggregate '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove aggregate '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
