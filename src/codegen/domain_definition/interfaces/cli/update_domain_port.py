"""
UpdateDomainPort command - Update an existing domain port in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_domain_port import (
    UpdateDomainPort,
    UpdateDomainPortCommand,
    UpdateDomainPortResult,
)


@inject
def _update_domain_port(
    cmd: UpdateDomainPortCommand,
    use_case: UpdateDomainPort = Provide[
        "domain_definition_container.update_domain_port"
    ],
) -> UpdateDomainPortResult:
    return use_case.execute(cmd)


def update_domain_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain port name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing domain port in a bounded context.
    """
    cmd = UpdateDomainPortCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_domain_port(cmd)
    if result.success:
        typer.echo(f"Successfully updated domain port '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update domain port '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
