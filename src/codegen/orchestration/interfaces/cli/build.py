"""
CLI build command - Compile codegen.yaml into Python code.
"""
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProject,
    GenerateProjectCommand,
)
from codegen.orchestration.domain.enums import BuildStatus, FileStatus
from codegen.orchestration.domain.value_objects.build_result import BuildResult
from dependency_injector.wiring import Provide, inject


console = Console()


def print_build_report(result: BuildResult) -> None:
    """Renders a human-friendly report of the build execution."""
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

    if result.files:
        table = Table(box=box.SIMPLE)
        table.add_column("Status", justify="center", style="bold")
        table.add_column("File Path", style="cyan")
        table.add_column("Message", style="dim")

        for file_res in result.files:
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
        console.print()

    stats = result.stats
    stats_text = Text()
    stats_text.append(f"Total Files: {stats.total_files} | ", style="bold")
    stats_text.append(f"Created: {stats.created_count} ", style="green")
    stats_text.append(f"Updated: {stats.updated_count} ", style="yellow")
    stats_text.append(f"Skipped: {stats.skipped_count} ", style="dim")
    stats_text.append(f"Failed: {stats.failed_count}", style="red" if stats.failed_count > 0 else "green")

    if stats.duration_ms > 0:
        stats_text.append(f" | Duration: {stats.duration_ms}ms", style="blue")

    console.print(Panel(stats_text, title="Statistics", border_style="blue"))

    if result.messages:
        console.print("\n[bold]Build Messages:[/bold]")
        for msg in result.messages:
            console.print(f"- {msg}")


@inject
def _generate_project(
    cmd: GenerateProjectCommand,
    use_case: GenerateProject = Provide[
        "orchestration_container.generate_project"
    ],
):
    result = use_case.execute(cmd)
    return result.result


def build(
    nodes: Annotated[Optional[list[str]], typer.Option("--node", "-n")] = None,
    generate_tests: Annotated[bool, typer.Option("--generate-tests")] = False,
) -> BuildResult:
    """
    Build: Compile codegen.yaml into Python code.
    """
    cmd = GenerateProjectCommand(
        nodes=nodes,
        generate_tests=generate_tests,
    )

    with console.status("[bold green]Generating code...[/]"):
        result = _generate_project(cmd)

    print_build_report(result)

    if result.status == BuildStatus.FAILURE:
        raise typer.Exit(code=1)

    return result
