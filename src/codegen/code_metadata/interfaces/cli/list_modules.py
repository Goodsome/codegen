import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from codegen.code_metadata.application.dtos.component_dto import ComponentDto
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.application.dtos.module_filter import ModuleFilter
from codegen.code_metadata.application.queries.list_components import ListComponents
from codegen.code_metadata.application.services.project_sync_service import ProjectSyncService
from codegen.code_metadata.domain.aggregates import Module
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery

console = Console()


@inject
def _list_modules(
    current: int,
    size: int,
    service: ProjectSyncService = Provide["code_metadata_container.project_sync_service"],
) -> Page[Module]:
    return service.list_modules()


def list_modules(
    page: Annotated[int, typer.Option("--page", "-p", help="Page number")] = 1,
    size: Annotated[int, typer.Option("--size", "-s", help="Page size")] = 10,
) -> None:
    """List components with optional filters and pagination."""
    result = _list_modules(current=page, size=size)

    for item in result.items:
        console.print(f"[bold]{item.name}-{item.id}[/bold] ({item.path})")
        # console.print(f"  {item.description}")

    console.print(
        f"\nPage {result.current} / {-(-result.total // result.size) if result.size else 0} (total: {result.total})"
    )
