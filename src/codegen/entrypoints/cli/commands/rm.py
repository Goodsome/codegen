"""
Remove command - Remove a value from blueprint by path.

New path-based command for deleting blueprint values.
"""

import typer
from codegen.entrypoints.cli.utils import get_container
from codegen.domain_definition.application.use_cases.remove_value import RemoveValueCommand

app = typer.Typer(name="rm", help="Remove a value from blueprint by path")


@app.command()
def rm(
    path: str = typer.Argument(
        ...,
        help="Path to remove (e.g., 'contexts.sales', 'contexts[0]')",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
):
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

    with get_container() as container:
        use_case = container.remove_value_use_case()
        try:
            use_case.execute(RemoveValueCommand(path=path))
            typer.echo(f"Successfully removed '{path}'")
        except KeyError as e:
            typer.echo(f"Error: Path not found - {e}", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
