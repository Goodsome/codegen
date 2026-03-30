"""
GetValueObject command - Get a value object from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_value_object import (
    GetValueObject,
    GetValueObjectQuery,
    GetValueObjectResult,
)


@inject
def _get_value_object(
    query: GetValueObjectQuery,
    use_case: GetValueObject = Provide["domain_definition_container.get_value_object"],
) -> GetValueObjectResult:
    return use_case.execute(query)


def get_value_object(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Value object name")],
) -> None:
    """
    Get a value object from a bounded context.
    """
    query = GetValueObjectQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_value_object(query)
    typer.echo(result.value_object.model_dump_json(indent=2))
