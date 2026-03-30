"""
UpdateCliCommand command - Update an existing CLI command in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_cli_command import (
    UpdateCliCommand,
    UpdateCliCommandCommand,
    UpdateCliCommandResult,
)


@inject
def _update_cli_command(
    cmd: UpdateCliCommandCommand,
    use_case: UpdateCliCommand = Provide[
        "domain_definition_container.update_cli_command"
    ],
) -> UpdateCliCommandResult:
    return use_case.execute(cmd)


def update_cli_command(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="CLI command name")],
    use_case: Annotated[str | None, typer.Option("--use-case", "-uc")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing CLI command in a bounded context.

    Examples:
        $ codegen interface update-cli-command Sales list-orders --description "Updated list orders command"
        $ codegen interface update-cli-command Billing create-invoice --use-case CreateNewInvoice
    """
    cmd = UpdateCliCommandCommand(
        context_name=context_name,
        name=name,
        use_case=use_case,
        description=description,
    )
    result = _update_cli_command(cmd)
    if result.success:
        typer.echo(f"Successfully updated CLI command '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update CLI command '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
