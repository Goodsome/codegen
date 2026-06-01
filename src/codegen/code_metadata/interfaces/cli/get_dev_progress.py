from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide, inject
from typer import Option

from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from codegen.code_metadata.application.services.dev_progress_service import DevProgressService

console = Console()


@inject
def _get_dev_progress(
    module_path: str | None,
    service: DevProgressService = Provide["code_metadata_container.dev_progress_service"],
) -> DevProgress:
    return service.get_dev_progress_v2(module_path=module_path)


def get_dev_progress(
    module_path: Annotated[str | None, Option( "--path", "-p" )] = None,
    component_type: Annotated[str | None, Option( "--type", "-t" )] = None,
) -> None:
    """Show development progress: AST similarity and line diffs per file."""
    result = _get_dev_progress(module_path=module_path)

    result.order_by_type()
    component_name = module_path.split(".")[-1] if module_path else None
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

    match_count = 0
    unknown_count = 0
    for r in result.records:
        if r.ast_similarity == 1:
            match_count += 1
            continue
        if r.component_type == "unknown":
            unknown_count += 1
        diff_sign = "+" if r.line_diff > 0 else ""
        console.print(
            f"  {r.file_name:<40} {r.component_type:<20} "
            + f"{r.ast_similarity:>5.1%} {r.original_lines:>6} "
            + f"{r.generated_lines:>6} {diff_sign}{r.line_diff:>5}"
        )

    console.print(
        "\n[bold]Dev Progress[/bold]  |  "
        + f"Matched Files: {match_count}/{len(result.records)}  |  "
        + f"AST Similarity: {result.ast_progress:.1%}  |  "
        + f"Unknown Files: {unknown_count}/{len(result.records)}"
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
