import typer
from codegen.domain_definition.application.use_cases.get_use_case import (
    GetUseCase,
    GetUseCaseQuery,
    GetUseCaseResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _get_use_case(
    cmd: GetUseCaseQuery,
    use_case: GetUseCase = Provide["domain_definition_container.get_use_case"],
) -> GetUseCaseResult:
    return use_case.execute(cmd)


def get_use_case(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Use case name")],
) -> None:
    """
    Get a use case from a bounded context.
    """
    query = GetUseCaseQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_use_case(query)
    typer.echo(result.use_case.model_dump_json(indent=2))
