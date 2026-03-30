"""
AddCliCommand command - Add a new CLI command to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_cli_command import (
    AddCliCommand,
    AddCliCommandCommand,
    AddCliCommandResult,
)


@inject
def _add_cli_command(
    cmd: AddCliCommandCommand,
    use_case: AddCliCommand = Provide["domain_definition_container.add_cli_command"],
) -> AddCliCommandResult:
    return use_case.execute(cmd)


def add_cli_command(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="CLI command name (kebab-case)")],
    use_case: Annotated[str, typer.Argument(help="Use case to execute")],
    description: Annotated[str, typer.Argument(help="Command description")],
) -> None:
    """
    Add a new CLI command to a bounded context.

    Examples:
        $ codegen interface add-cli-command Sales list-orders ListOrders "List all orders"
        $ codegen interface add-cli-command Billing create-invoice CreateInvoice "Create a new invoice"
    """
    cmd = AddCliCommandCommand(
        context_name=context_name,
        name=name,
        use_case=use_case,
        description=description,
    )
    result = _add_cli_command(cmd)
    if result.success:
        typer.echo(f"Successfully added CLI command '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add CLI command '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
