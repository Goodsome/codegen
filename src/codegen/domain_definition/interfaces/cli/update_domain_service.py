"""
UpdateDomainService command - Update an existing domain service in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_domain_service import (
    UpdateDomainService,
    UpdateDomainServiceCommand,
    UpdateDomainServiceResult,
)


@inject
def _update_domain_service(
    cmd: UpdateDomainServiceCommand,
    use_case: UpdateDomainService = Provide[
        "domain_definition_container.update_domain_service"
    ],
) -> UpdateDomainServiceResult:
    return use_case.execute(cmd)


def update_domain_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain service name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing domain service in a bounded context.
    """
    cmd = UpdateDomainServiceCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_domain_service(cmd)
    if result.success:
        typer.echo(f"Successfully updated domain service '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update domain service '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
