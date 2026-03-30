"""
RemoveCliCommand command - Remove a CLI command from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_cli_command import (
    RemoveCliCommand,
    RemoveCliCommandCommand,
    RemoveCliCommandResult,
)


@inject
def _remove_cli_command(
    cmd: RemoveCliCommandCommand,
    use_case: RemoveCliCommand = Provide[
        "domain_definition_container.remove_cli_command"
    ],
) -> RemoveCliCommandResult:
    return use_case.execute(cmd)


def remove_cli_command(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="CLI command name")],
) -> None:
    """
    Remove a CLI command from a bounded context.

    Examples:
        $ codegen interface remove-cli-command Sales list-orders
        $ codegen interface remove-cli-command Billing create-invoice
    """
    cmd = RemoveCliCommandCommand(context_name=context_name, name=name)
    result = _remove_cli_command(cmd)
    if result.success:
        typer.echo(f"Successfully removed CLI command '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove CLI command '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
