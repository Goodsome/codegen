"""
Build command - Compile codegen.yaml into Python code.

Replaces the old 'codegen generate' command.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from codegen.cli.utils import get_container
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
from codegen.orchestration.domain.enums import BuildStatus, FileStatus
from codegen.orchestration.domain.value_objects.build_result import BuildResult

app = typer.Typer(name="build", help="Build Python code from blueprint")
console = Console()


def print_build_report(result: BuildResult):
    """
    Renders a human-friendly report of the build execution.
    """
    # 1. Determine Header Color based on Status
    status_style = "green"
    if result.status == BuildStatus.WARNING:
        status_style = "yellow"
    elif result.status == BuildStatus.FAILURE:
        status_style = "red"

    console.print(
        Panel(
            f"Build Finished with status: [{status_style} bold]{result.status.value}[/]",
            title="Build Summary",
            expand=False,
            border_style=status_style,
        )
    )

    # 2. Create File Detail Table
    if result.files:
        table = Table(box=box.SIMPLE)
        table.add_column("Status", justify="center", style="bold")
        table.add_column("File Path", style="cyan")
        table.add_column("Message", style="dim")

        for file_res in result.files:
            # Map status to icon/color
            if file_res.status == FileStatus.CREATED:
                status_str = "[green]CREATED[/]"
                icon = "✨"
            elif file_res.status == FileStatus.UPDATED:
                status_str = "[yellow]UPDATED[/]"
                icon = "📝"
            elif file_res.status == FileStatus.SKIPPED:
                status_str = "[dim]SKIPPED[/]"
                icon = "⏭️ "
            elif file_res.status == FileStatus.FAILED:
                status_str = "[red]FAILED[/]"
                icon = "❌"
            else:
                status_str = str(file_res.status.value)
                icon = ""

            table.add_row(
                f"{icon} {status_str}",
                file_res.path,
                file_res.message or "-"
            )

        console.print(table)
        console.print()  # Spacer

    # 3. Print Stats
    stats = result.stats
    stats_text = Text()
    stats_text.append(f"Total Files: {stats.total_files} | ", style="bold")
    stats_text.append(f"Created: {stats.created_count} ", style="green")
    stats_text.append(f"Updated: {stats.updated_count} ", style="yellow")
    stats_text.append(f"Skipped: {stats.skipped_count} ", style="dim")
    stats_text.append(f"Failed: {stats.failed_count}", style="red" if stats.failed_count > 0 else "green")

    # If duration is available (assuming BuildStats has logic to track it, otherwise 0)
    if stats.duration_ms > 0:
        stats_text.append(f" | Duration: {stats.duration_ms}ms", style="blue")

    console.print(Panel(stats_text, title="Statistics", border_style="blue"))

    # 4. Print Global Messages (if any)
    if result.messages:
        console.print("\n[bold]Build Messages:[/bold]")
        for msg in result.messages:
            console.print(f"- {msg}")


@app.command()
def build(
        overwrite: bool = typer.Option(
            False, "--overwrite", help="Overwrite existing files without prompting"
        ),
        build_dir: bool = typer.Option(
            True,
            "--build/--no-build",
            help="Output to src directory (default: --build). Use --no-build to output to target directory",
        ),
        node: Optional[str] = typer.Option(
            None,
            "--node",
            help="Generate only a specific bounded context or component by name (e.g., 'DomainDefinition')",
        ),
        config_file: Path = typer.Option(
            Path("codegen.yaml"),
            "--config",
            "-c",
            help="Path to the codegen.yaml blueprint file",
        ),
        out: Path | None = typer.Option(
            None,
            "--out",
            help="Custom output directory (overrides --build/--no-build default locations)",
        ),
):
    """
    Build: Compile codegen.yaml into Python code.
    
    This is the primary code generation command. It reads your blueprint
    file and generates Python code based on DDD patterns.
    
    Examples:
        $ codegen build
        $ codegen build --overwrite
        $ codegen build --node DomainDefinition
        $ codegen build --no-build --out ./generated
    """
    subdir = "src" if build_dir else "target"

    # Using specific error handling style or just standard flow
    with get_container(config_file=config_file, out=out, subdir=subdir) as container:
        use_case = container.generate_project_use_case()

        if node is not None:
            # Logic from original code: imply overwrite if node is specific
            overwrite = True

        root_path = ""
        if out:
            root_path = str(out).replace("/", ".").replace("\\", ".")

        cmd = GenerateProjectCommand(overwrite=overwrite, node=node, root_path=root_path)

        # --- Change Starts Here ---
        try:
            with console.status("[bold green]Generating code...[/]"):
                project_result = use_case.execute(cmd)

            # The use_case returns GenerateProjectResult, containing a .result (BuildResult)
            print_build_report(project_result.result)

            if project_result.result.status == BuildStatus.FAILURE:
                raise typer.Exit(code=1)

        except Exception as e:
            console.print_exception()
            typer.echo(f"An error occurred: {e}")
            raise typer.Exit(code=1)
        # --- Change Ends Here ---