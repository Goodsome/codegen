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

from codegen.entrypoints.cli.utils import get_container
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
from codegen.orchestration.domain.enums import BuildStatus, FileStatus
from codegen.orchestration.domain.value_objects.build_result import BuildResult

app = typer.Typer(name="build", help="Build Python code from blueprint")
console = Console()


def parse_nodes(nodes_str: str | None) -> list[str] | None:
    """Parse comma-separated node string into a list."""
    if nodes_str is None:
        return None
    return [n.strip() for n in nodes_str.split(",") if n.strip()]


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
    node: Optional[str] = typer.Option(
        None,
        "--node",
        help="Generate only specific bounded contexts or components by name, comma-separated (e.g., 'DomainDefinition' or 'AggregateSpec,EntitySpec')",
    ),
    generate_tests: bool = typer.Option(
        False,
        "--generate-tests",
        help="Generate unit test skeletons (skipped by default)",
    ),
):
    """
    Build: Compile codegen.yaml into Python code.

    This is the primary code generation command. It reads your blueprint
    file and generates Python code based on DDD patterns.

    When --node is specified, overwrite mode is automatically enabled.

    Examples:
        $ codegen build
        $ codegen build --node DomainDefinition
        $ codegen build --node AggregateSpec,EntitySpec,ValueObjectSpec
    """
    with get_container() as container:
        use_case = container.generate_project_use_case()

        nodes = parse_nodes(node)

        cmd = GenerateProjectCommand(
            nodes=nodes,
            root_path="",  # Modern src layout: import paths don't include src prefix
            generate_tests=generate_tests,
        )

        try:
            with console.status("[bold green]Generating code...[/]"):
                project_result = use_case.execute(cmd)

            print_build_report(project_result.result)

            if project_result.result.status == BuildStatus.FAILURE:
                raise typer.Exit(code=1)

        except Exception as e:
            console.print_exception()
            typer.echo(f"An error occurred: {e}")
            raise typer.Exit(code=1)