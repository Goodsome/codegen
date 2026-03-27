"""
Remove Context command - Remove a bounded context from the blueprint.
"""
import typer
from dependency_injector.wiring import Provide, inject
from codegen.domain_definition.application.use_cases.remove_context import (
    RemoveContext,
    RemoveContextCommand,
    RemoveContextResult,
)
from typing import Annotated


@inject
def _remove_context(
    cmd: RemoveContextCommand,
    use_case: RemoveContext = Provide["domain_definition_container.remove_context"],
) -> RemoveContextResult:
    return use_case.execute(cmd)


def remove_context(
    name: Annotated[str, typer.Argument(
        ...,
        help="Context name to remove (e.g., 'Billing', 'OrderManagement')",
    )],
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
) -> None:
    """
    Remove Context: Delete a bounded context from the blueprint.

    Examples:
        $ codegen remove-context Billing
        $ codegen remove-context "OrderManagement" --force
    """
    if not force:
        confirm = typer.confirm(f"Are you sure you want to remove context '{name}'?")
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

    cmd = RemoveContextCommand(name=name)
    _remove_context(cmd)
    typer.echo(f"Removed context '{name}'")
