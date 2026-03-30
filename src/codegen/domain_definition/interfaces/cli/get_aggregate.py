"""
GetAggregate command - Get an aggregate from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_aggregate import (
    GetAggregate,
    GetAggregateQuery,
    GetAggregateResult,
)


@inject
def _get_aggregate(
    query: GetAggregateQuery,
    use_case: GetAggregate = Provide["domain_definition_container.get_aggregate"],
) -> GetAggregateResult:
    return use_case.execute(query)


def get_aggregate(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Aggregate name")],
) -> None:
    """
    Get an aggregate from a bounded context.
    """
    query = GetAggregateQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_aggregate(query)
    typer.echo(result.aggregate.model_dump_json(indent=2))
