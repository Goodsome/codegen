"""RemoveDomainEvent command - Remove a domain event from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_domain_event import (
    RemoveDomainEvent,
    RemoveDomainEventCommand,
    RemoveDomainEventResult,
)


@inject
def _remove_domain_event(
    cmd: RemoveDomainEventCommand,
    use_case: RemoveDomainEvent = Provide[
        "domain_definition_container.remove_domain_event"
    ],
) -> RemoveDomainEventResult:
    return use_case.execute(cmd)


def remove_domain_event(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain event name")],
) -> None:
    """
    Remove a domain event from a bounded context.
    """
    cmd = RemoveDomainEventCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_domain_event(cmd)
    if result.success:
        typer.echo(f"Successfully removed domain event '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove domain event '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
