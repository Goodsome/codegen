"""GetRepository command - Get a repository from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_repository import (
    GetRepository,
    GetRepositoryQuery,
    GetRepositoryResult,
)


@inject
def _get_repository(
    query: GetRepositoryQuery,
    use_case: GetRepository = Provide[
        "domain_definition_container.get_repository"
    ],
) -> GetRepositoryResult:
    return use_case.execute(query)


def get_repository(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Repository name")],
) -> None:
    """
    Get a repository from a bounded context.
    """
    query = GetRepositoryQuery(context_name=context_name, name=name)
    result = _get_repository(query)
    typer.echo(result.repository.model_dump_json(indent=2))
