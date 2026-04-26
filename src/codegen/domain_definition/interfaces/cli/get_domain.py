"""GetDomain command - Get the domain spec from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_domain import (
    GetDomain,
    GetDomainQuery,
    GetDomainResult,
)


@inject
def _get_domain(
    query: GetDomainQuery,
    use_case: GetDomain = Provide["domain_definition_container.get_domain"],
) -> GetDomainResult:
    return use_case.execute(query)


def get_domain(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
) -> None:
    """
    Get the domain spec from a bounded context.
    """
    query = GetDomainQuery(context_name=context_name)
    result = _get_domain(query)
    
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=f"Domain Specification: [bold cyan]{context_name}[/bold cyan]")
    table.add_column("Type", style="green", no_wrap=True)
    table.add_column("Name", style="bold magenta")

    domain = result.domain
    
    # Mapping of domain attributes to their display labels
    sections = [
        (domain.aggregates, "Aggregate"),
        (domain.entities, "Entity"),
        (domain.value_objects, "Value Object"),
        (domain.enums, "Enum"),
        (domain.services, "Service"),
        (domain.ports, "Port"),
        (domain.domain_events, "Domain Event"),
        (domain.domain_exceptions, "Domain Exception"),
        (domain.repositories, "Repository"),
        (domain.core, "Core"),
    ]

    found_any = False
    for items, label in sections:
        for item in items:
            table.add_row(label, str(item.name))
            found_any = True

    if not found_any:
        console.print(f"[yellow]No domain concepts found in context '{context_name}'.[/yellow]")
    else:
        console.print(table)
