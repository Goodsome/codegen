"""UpdateDomainEvent command - Update an existing domain event in a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_domain_event import (
    UpdateDomainEvent,
    UpdateDomainEventCommand,
    UpdateDomainEventResult,
)


@inject
def _update_domain_event(
    cmd: UpdateDomainEventCommand,
    use_case: UpdateDomainEvent = Provide[
        "domain_definition_container.update_domain_event"
    ],
) -> UpdateDomainEventResult:
    return use_case.execute(cmd)


def update_domain_event(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain event name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing domain event in a bounded context.
    """
    cmd = UpdateDomainEventCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_domain_event(cmd)
    if result.success:
        typer.echo(f"Successfully updated domain event '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update domain event '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
