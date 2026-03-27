"""
Remove command - Remove a value from blueprint by path.
"""
import typer
from codegen.domain_definition.application.use_cases.remove_value import (
    RemoveValue,
    RemoveValueCommand,
    RemoveValueResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _remove_value(
    cmd: RemoveValueCommand,
    use_case: RemoveValue = Provide[
        "domain_definition_container.remove_value"
    ],
) -> RemoveValueResult:
    return use_case.execute(cmd)


def rm(
    path: Annotated[str, typer.Argument(
        ...,
        help="Path to remove (e.g., 'contexts.sales', 'contexts[0]')",
    )],
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
) -> None:
    """
    Remove: Delete a value from blueprint by path.

    Use dot notation to specify what to remove.
    Can remove fields, list items (by index or name), or nested objects.

    Examples:
        $ codegen rm "contexts.Sales"
        $ codegen rm "contexts[0]"
        $ codegen rm "contexts.DomainDefinition.domain.aggregates.Order"
        $ codegen rm "contexts.DomainDefinition.description"
    """
    if not force:
        confirm = typer.confirm(f"Are you sure you want to remove '{path}'?")
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

    cmd = RemoveValueCommand(path=path)
    _remove_value(cmd)
    typer.echo(f"Successfully removed '{path}'")
