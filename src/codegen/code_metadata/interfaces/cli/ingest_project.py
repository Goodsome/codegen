import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from codegen.code_metadata.application.commands.ingest_project import IngestProject
from codegen.code_metadata.application.dtos.ingest_project_command import (
    IngestProjectCommand,
)

console = Console()


@inject
def _ingest_project(
    cmd: IngestProjectCommand,
    use_case: IngestProject = Provide["code_metadata_container.ingest_project"],
) -> None:
    result = use_case.execute(cmd)
    console.print(
        f"[green]Ingest complete:[/green] "
        f"{result.nodes_created} nodes synced, "
        f"{result.nodes_deleted} stale nodes removed."
    )


def ingest_project(
    context_name: Annotated[
        str, typer.Argument(help="The bounded context name to ingest, e.g. code_metadata")
    ],
) -> None:
    """Scan a bounded context's directory tree into the CodeNode graph."""
    cmd = IngestProjectCommand(context_name=context_name)
    try:
        _ingest_project(cmd)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
