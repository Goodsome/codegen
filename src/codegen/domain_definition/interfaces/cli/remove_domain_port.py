"""
RemoveDomainPort command - Remove a domain port from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_domain_port import (
    RemoveDomainPort,
    RemoveDomainPortCommand,
    RemoveDomainPortResult,
)


@inject
def _remove_domain_port(
    cmd: RemoveDomainPortCommand,
    use_case: RemoveDomainPort = Provide[
        "domain_definition_container.remove_domain_port"
    ],
) -> RemoveDomainPortResult:
    return use_case.execute(cmd)


def remove_domain_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain port name")],
) -> None:
    """
    Remove a domain port from a bounded context.
    """
    cmd = RemoveDomainPortCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_domain_port(cmd)
    if result.success:
        typer.echo(f"Successfully removed domain port '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove domain port '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
