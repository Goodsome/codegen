"""
Init command - Initialize a new codegen.yaml blueprint.
"""

from pathlib import Path

import typer
from rich.console import Console

from codegen.entrypoints.cli.utils import get_container
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from codegen.domain_definition.domain.entities.bounded_context import BoundedContext

app = typer.Typer(name="init", help="Initialize a new codegen.yaml blueprint")
console = Console()

@app.command()
def init():
    """
    Init: Initialize a new codegen.yaml blueprint.

    This command creates a new, default blueprint file with a 'Shared' context
    in the current directory.

    Examples:
        $ codegen init
    """
    config_file_path = Path.cwd() / "codegen.yaml"

    if config_file_path.exists():
        console.print(f"[bold red]Error:[/] The file [yellow]{config_file_path}[/] already exists. Initialization aborted.", style="red")
        raise typer.Exit(code=1)

    project_name = Path.cwd().name

    # Create default contexts
    shared_context = BoundedContext.create(name="Shared", description="Common generic components.")

    # Create the blueprint
    blueprint = Blueprint.create(
        name=project_name,
        description=f"{project_name} project",
        contexts=[shared_context],
    )

    with get_container() as container:
        # Resolve the storage directly from the container
        storage = container.blueprint_loader_provider()
        storage.save(blueprint)

    console.print(f"[bold green]Success:[/] Initialized a new project blueprint at [yellow]{config_file_path}[/]")
