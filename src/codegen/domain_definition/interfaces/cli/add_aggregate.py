"""
AddAggregate command - Add a new aggregate to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_aggregate import (
    AddAggregate,
    AddAggregateCommand,
    AddAggregateResult,
)


@inject
def _add_aggregate(
    cmd: AddAggregateCommand,
    use_case: AddAggregate = Provide["domain_definition_container.add_aggregate"],
) -> AddAggregateResult:
    return use_case.execute(cmd)


def add_aggregate(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Aggregate name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Aggregate description")],
) -> None:
    """
    Add a new aggregate to a bounded context.

    Examples:
        $ codegen domain add-aggregate Sales Order "Customer order aggregate"
        $ codegen domain add-aggregate Billing Invoice "Billing invoice aggregate"
    """
    cmd = AddAggregateCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_aggregate(cmd)
    if result.success:
        typer.echo(f"Successfully added aggregate '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add aggregate '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
