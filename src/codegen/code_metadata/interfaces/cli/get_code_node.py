from typing import Annotated
from uuid import UUID

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDetailDto
from codegen.code_metadata.application.queries.get_code_node_detail import GetCodeNodeDetail

console = Console()


@inject
def _get_code_node_detail(
    node_id: UUID,
    use_case: GetCodeNodeDetail = Provide["code_metadata_container.get_code_node_detail"],
) -> CodeNodeDetailDto:
    return use_case.execute(node_id)


def get_code_node(
    id: Annotated[str, typer.Argument(help="UUID of the CodeNode")],
) -> None:
    """Display detailed information about a CodeNode by its ID."""
    try:
        node_id = UUID(id)
    except ValueError:
        console.print(f"[red]Error: '{id}' is not a valid UUID[/red]")
        raise typer.Exit(1)

    try:
        detail = _get_code_node_detail(node_id)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # ── 基本信息面板 ──
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")
    info_table.add_row("ID", str(detail.id))
    info_table.add_row("FQN", detail.fqn)
    info_table.add_row("Name", detail.name)
    info_table.add_row("Kind", detail.kind.value)
    info_table.add_row("Description", detail.description or "[dim]N/A[/dim]")
    if detail.properties:
        for key, value in detail.properties.items():
            info_table.add_row(f"Property.{key}", str(value))

    console.print(Panel(info_table, title="[bold]CodeNode Detail[/bold]", border_style="blue"))

    # ── 出边表格 ──
    if detail.outbound_edges:
        out_table = Table(title="Outbound Edges", show_lines=True)
        out_table.add_column("Type", style="cyan")
        out_table.add_column("Target FQN", style="green")
        for edge in detail.outbound_edges:
            out_table.add_row(edge.type.value, edge.target_fqn)
        console.print(out_table)
    else:
        console.print("[dim]No outbound edges[/dim]")

    # ── 入边表格 ──
    if detail.inbound_edges:
        in_table = Table(title="Inbound Edges", show_lines=True)
        in_table.add_column("Type", style="cyan")
        in_table.add_column("Source FQN", style="green")
        for edge in detail.inbound_edges:
            in_table.add_row(edge.type.value, edge.source_fqn)
        console.print(in_table)
    else:
        console.print("[dim]No inbound edges[/dim]")
