"""GetDomainEvent command - Get a domain event from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_domain_event import (
    GetDomainEvent,
    GetDomainEventQuery,
    GetDomainEventResult,
)


@inject
def _get_domain_event(
    query: GetDomainEventQuery,
    use_case: GetDomainEvent = Provide[
        "domain_definition_container.get_domain_event"
    ],
) -> GetDomainEventResult:
    return use_case.execute(query)


def get_domain_event(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain event name")],
) -> None:
    """
    Get a domain event from a bounded context.
    """
    query = GetDomainEventQuery(context_name=context_name, name=name)
    result = _get_domain_event(query)
    typer.echo(result.domain_event.model_dump_json(indent=2))
