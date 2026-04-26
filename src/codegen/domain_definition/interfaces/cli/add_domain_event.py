"""AddDomainEvent command - Add a new domain event to a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_domain_event import (
    AddDomainEvent,
    AddDomainEventCommand,
    AddDomainEventResult,
)


@inject
def _add_domain_event(
    cmd: AddDomainEventCommand,
    use_case: AddDomainEvent = Provide[
        "domain_definition_container.add_domain_event"
    ],
) -> AddDomainEventResult:
    return use_case.execute(cmd)


def add_domain_event(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain event name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Domain event description")],
) -> None:
    """
    Add a new domain event to a bounded context.
    """
    cmd = AddDomainEventCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_domain_event(cmd)
    if result.success:
        typer.echo(f"Successfully added domain event '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add domain event '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
