import typer
from codegen.domain_definition.application.use_cases.get_app_port import (
    GetAppPort,
    GetAppPortQuery,
    GetAppPortResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _get_app_port(
    cmd: GetAppPortQuery,
    use_case: GetAppPort = Provide["domain_definition_container.get_app_port"],
) -> GetAppPortResult:
    return use_case.execute(cmd)


def get_app_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App port name")],
) -> None:
    """
    Get an app port from a bounded context.
    """
    query = GetAppPortQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_app_port(query)
    typer.echo(result.port.model_dump_json(indent=2))
