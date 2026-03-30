"""
AddDomainService command - Add a new domain service to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_domain_service import (
    AddDomainService,
    AddDomainServiceCommand,
    AddDomainServiceResult,
)


@inject
def _add_domain_service(
    cmd: AddDomainServiceCommand,
    use_case: AddDomainService = Provide[
        "domain_definition_container.add_domain_service"
    ],
) -> AddDomainServiceResult:
    return use_case.execute(cmd)


def add_domain_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain service name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Domain service description")],
) -> None:
    """
    Add a new domain service to a bounded context.
    """
    cmd = AddDomainServiceCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_domain_service(cmd)
    if result.success:
        typer.echo(f"Successfully added domain service '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add domain service '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
