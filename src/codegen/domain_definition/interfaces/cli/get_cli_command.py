"""
GetCliCommand command - Get a CLI command from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_cli_command import (
    GetCliCommand,
    GetCliCommandQuery,
    GetCliCommandResult,
)


@inject
def _get_cli_command(
    cmd: GetCliCommandQuery,
    use_case: GetCliCommand = Provide["domain_definition_container.get_cli_command"],
) -> GetCliCommandResult:
    return use_case.execute(cmd)


def get_cli_command(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="CLI command name")],
) -> None:
    """
    Get a CLI command from a bounded context.

    Examples:
        $ codegen interface get-cli-command Sales list-orders
        $ codegen interface get-cli-command Billing create-invoice
    """
    cmd = GetCliCommandQuery(context_name=context_name, name=name)
    result = _get_cli_command(cmd)
    typer.echo(result.cli_command.model_dump_json(indent=2))
