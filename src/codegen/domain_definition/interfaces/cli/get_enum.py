"""
GetEnum command - Get an enum from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_enum import (
    GetEnum,
    GetEnumQuery,
    GetEnumResult,
)


@inject
def _get_enum(
    query: GetEnumQuery,
    use_case: GetEnum = Provide["domain_definition_container.get_enum"],
) -> GetEnumResult:
    return use_case.execute(query)


def get_enum(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Enum name")],
) -> None:
    """
    Get an enum from a bounded context.
    """
    query = GetEnumQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_enum(query)
    typer.echo(result.enum.model_dump_json(indent=2))
