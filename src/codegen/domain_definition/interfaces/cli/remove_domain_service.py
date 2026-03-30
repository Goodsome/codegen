"""
RemoveDomainService command - Remove a domain service from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_domain_service import (
    RemoveDomainService,
    RemoveDomainServiceCommand,
    RemoveDomainServiceResult,
)


@inject
def _remove_domain_service(
    cmd: RemoveDomainServiceCommand,
    use_case: RemoveDomainService = Provide[
        "domain_definition_container.remove_domain_service"
    ],
) -> RemoveDomainServiceResult:
    return use_case.execute(cmd)


def remove_domain_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain service name")],
) -> None:
    """
    Remove a domain service from a bounded context.
    """
    cmd = RemoveDomainServiceCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_domain_service(cmd)
    if result.success:
        typer.echo(f"Successfully removed domain service '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove domain service '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
