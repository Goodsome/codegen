"""
GetEntity command - Get an entity from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_entity import (
    GetEntity,
    GetEntityQuery,
    GetEntityResult,
)


@inject
def _get_entity(
    query: GetEntityQuery,
    use_case: GetEntity = Provide["domain_definition_container.get_entity"],
) -> GetEntityResult:
    return use_case.execute(query)


def get_entity(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Entity name")],
) -> None:
    """
    Get an entity from a bounded context.
    """
    query = GetEntityQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_entity(query)
    typer.echo(result.entity.model_dump_json(indent=2))
