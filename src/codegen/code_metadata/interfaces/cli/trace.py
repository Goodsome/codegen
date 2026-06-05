from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.tree import Tree

from codegen.code_metadata.application.dtos.graph_view import GraphViewNode
from codegen.code_metadata.application.dtos.trace_query import TraceSymbolDependenciesQuery
from codegen.code_metadata.application.queries.trace_symbol_dependencies import (
    TraceSymbolDependenciesQueryHandler,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType

console = Console()

KIND_ICONS = {
    CodeNodeKind.DIRECTORY: "📁",
    CodeNodeKind.FILE: "📄",
    CodeNodeKind.MODULE: "📦",
    CodeNodeKind.CLASS: "🏢",
    CodeNodeKind.FUNCTION: "⚡",
    CodeNodeKind.METHOD: "⚡",
    CodeNodeKind.VARIABLE: "🔶",
    CodeNodeKind.EXTERNAL: "🔌",
}

EDGE_LABELS = {
    EdgeType.IMPORTS: "IMPORTS",
    EdgeType.INHERITS: "INHERITS",
    EdgeType.IMPLEMENTS: "IMPLEMENTS",
    EdgeType.INSTANTIATES: "INSTANTIATES",
    EdgeType.CALLS: "CALLS",
    EdgeType.REFERENCES: "REFERENCES",
    EdgeType.EXPORTS: "EXPORTS",
    EdgeType.CONTAINS: "CONTAINS",
}


def _validate_direction(value: str) -> str:
    if value not in ("upstream", "downstream"):
        raise typer.BadParameter("direction must be 'upstream' or 'downstream'")
    return value


@inject
def _trace_symbol_dependencies(
    query: TraceSymbolDependenciesQuery,
    handler: TraceSymbolDependenciesQueryHandler = Provide[
        "code_metadata_container.trace_symbol_dependencies"
    ],
) -> GraphViewNode:
    result = handler.execute(query)
    return result.root


def _is_external(node) -> bool:
    return node.kind == CodeNodeKind.EXTERNAL or "." not in node.fqn


def _node_label(node) -> str:
    icon = KIND_ICONS.get(node.kind, "❓")
    suffix = " (External)" if _is_external(node) else ""
    return f"{icon} {node.kind.value.capitalize()}: {node.fqn}{suffix}"


def _render_node(parent: Tree, gv_node: GraphViewNode, *, is_last: bool) -> None:
    if gv_node.node is None:
        # 分组节点（如 "⚡ Calls:"）
        edge_label = EDGE_LABELS.get(gv_node.edge_type, str(gv_node.edge_type))
        section = parent.add(
            f"⚡ {edge_label}:",
            guide_style="bold cyan",
        )
        _render_children(section, gv_node.children)
        return

    label = _node_label(gv_node.node)
    if gv_node.edge_type is not None:
        edge_label = EDGE_LABELS.get(gv_node.edge_type, str(gv_node.edge_type))
        label = f"➔ [{edge_label}] {label}"

    branch = parent.add(label, guide_style="bold green" if is_last else "dim")
    _render_children(branch, gv_node.children)


def _render_children(parent: Tree, children: list[GraphViewNode]) -> None:
    for i, child in enumerate(children):
        _render_node(parent, child, is_last=i == len(children) - 1)


def trace(
    fqn: Annotated[str, typer.Option("--fqn", help="Fully qualified name of the target symbol")],
    direction: Annotated[
        str,
        typer.Option("--direction", "-d", help="Trace direction: upstream or downstream"),
    ] = "upstream",
    edge_type: Annotated[
        str | None,
        typer.Option("--edge-type", "-e", help="Filter by edge type (e.g. imports, calls, inherits)"),
    ] = None,
) -> None:
    """Trace symbol dependencies in the code graph."""
    direction = _validate_direction(direction)

    parsed_edge_type = EdgeType(edge_type) if edge_type else None
    query = TraceSymbolDependenciesQuery(target_fqn=fqn, direction=direction, edge_type=parsed_edge_type)

    try:
        root = _trace_symbol_dependencies(query)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    if root.node is None:
        console.print("[yellow]No dependencies found.[/yellow]")
        return

    tree = Tree(_node_label(root.node))
    _render_children(tree, root.children)
    console.print(tree)
