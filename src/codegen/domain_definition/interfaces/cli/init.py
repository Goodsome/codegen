"""
Init command - Initialize a new codegen.yaml blueprint.
"""
from pathlib import Path
from typing import Annotated, Optional

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from codegen.domain_definition.application.use_cases.init_project import (
    InitProject,
    InitProjectCommand,
)


app = typer.Typer(name="init", help="Initialize a new codegen.yaml blueprint")
console = Console()


@inject
def _init_project(
    cmd: InitProjectCommand,
    use_case: InitProject = Provide["domain_definition_container.init_project"],
) -> None:
    return use_case.execute(cmd)


def init(
    project_name: Annotated[Optional[str], typer.Option("--name", "-n", help="Project name")] = None,
    project_description: Annotated[Optional[str], typer.Option("--description", "-d", help="Project description")] = None,
) -> None:
    """
    Init: Initialize a new codegen.yaml blueprint.

    This command creates a new, default blueprint file with a 'Shared' context
    in the current directory.

    Examples:
        $ codegen init
        $ codegen init --name MyProject --description "My awesome project"
    """
    config_file_path = Path.cwd() / "codegen.yaml"

    if config_file_path.exists():
        console.print(f"[bold red]Error:[/] The file [yellow]{config_file_path}[/] already exists. Initialization aborted.", style="red")
        raise typer.Exit(code=1)

    # Use current directory name as default project name
    if project_name is None:
        project_name = Path.cwd().name

    cmd = InitProjectCommand(
        project_name=project_name,
        project_description=project_description,
    )
    _init_project(cmd)

    console.print(f"[bold green]Success:[/] Initialized a new project blueprint at [yellow]{config_file_path}[/]")
