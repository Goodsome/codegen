from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide, inject
from typer import Argument, Option

from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from codegen.code_metadata.application.dtos.get_dev_progress_query import GetDevProgressQuery
from codegen.code_metadata.application.queries.get_dev_progress import GetDevProgress

console = Console()


@inject
def _get_dev_progress(
    query: GetDevProgressQuery,
    use_case: GetDevProgress = Provide["code_metadata_container.get_dev_progress"],
) -> DevProgress:
    return use_case.execute(query=query)


def get_dev_progress(
    context: Annotated[str, Argument()],
    component_type: Annotated[str | None, Option( "--type", "-t" )] = None,
    component_name: Annotated[str | None, Option( "--name", "-n" )] = None,
) -> None:
    """Show development progress: AST similarity and line diffs per file."""
    query = GetDevProgressQuery(
        context=context,
        component_type=component_type,
    )
    result = _get_dev_progress(query=query)

    result.order_by_type()
    if component_type:
        result = result.filter_by_type(component_type)
    if component_name:
        result = result.filter_by_name(component_name)

    if not result.records:
        console.print("[yellow]No component records found.[/yellow]")
        return

    console.print(
        f"  {'File':<40} {'Type':<20} {'AST':>6} {'Orig':>6} {'Gen':>6} {'Diff':>6}"
    )
    console.print("  " + "-" * 76)

    for r in result.records:
        diff_sign = "+" if r.line_diff > 0 else ""
        console.print(
            f"  {r.file_name:<40} {r.component_type:<20} "
            + f"{r.ast_similarity:>5.1%} {r.original_lines:>6} "
            + f"{r.generated_lines:>6} {diff_sign}{r.line_diff:>5}"
        )

    console.print(
        "\n[bold]Dev Progress[/bold]  |  "
        + f"Files: {len(result.records)}  |  "
        + f"AST Similarity: {result.ast_progress:.1%}\n"
    )

    if component_name:
        record = result.get_record_by_name(component_name)
        if record:
            console.print(f"  {record.file_name:<40} {record.component_type:<20} " )
            console.print("-" * 76)
            console.print(f"{record.original_code}")
            console.print("-" * 76)
            console.print(f"{record.generated_code}")
            console.print("-" * 76)
        else:
            console.print(f"[yellow]No record found for component name: {component_name}[/yellow]")
