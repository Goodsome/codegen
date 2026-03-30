"""
AddDomainPort command - Add a new domain port to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_domain_port import (
    AddDomainPort,
    AddDomainPortCommand,
    AddDomainPortResult,
)


@inject
def _add_domain_port(
    cmd: AddDomainPortCommand,
    use_case: AddDomainPort = Provide["domain_definition_container.add_domain_port"],
) -> AddDomainPortResult:
    return use_case.execute(cmd)


def add_domain_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain port name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Domain port description")],
) -> None:
    """
    Add a new domain port to a bounded context.
    """
    cmd = AddDomainPortCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_domain_port(cmd)
    if result.success:
        typer.echo(f"Successfully added domain port '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add domain port '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
