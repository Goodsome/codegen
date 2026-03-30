import typer
from codegen.domain_definition.application.use_cases.get_app_service import (
    GetAppService,
    GetAppServiceQuery,
    GetAppServiceResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _get_app_service(
    cmd: GetAppServiceQuery,
    use_case: GetAppService = Provide["domain_definition_container.get_app_service"],
) -> GetAppServiceResult:
    return use_case.execute(cmd)


def get_app_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App service name")],
) -> None:
    """
    Get an app service from a bounded context.
    """
    query = GetAppServiceQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_app_service(query)
    typer.echo(result.service.model_dump_json(indent=2))
