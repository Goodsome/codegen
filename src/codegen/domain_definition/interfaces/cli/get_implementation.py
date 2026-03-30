"""
GetImplementation command - Get an implementation from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_implementation import (
    GetImplementation,
    GetImplementationQuery,
    GetImplementationResult,
)


@inject
def _get_implementation(
    cmd: GetImplementationQuery,
    use_case: GetImplementation = Provide[
        "domain_definition_container.get_implementation"
    ],
) -> GetImplementationResult:
    return use_case.execute(cmd)


def get_implementation(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Implementation name")],
) -> None:
    """
    Get an implementation from a bounded context.

    Examples:
        $ codegen infrastructure get-implementation Sales postgres
        $ codegen infrastructure get-implementation Billing stripe
    """
    cmd = GetImplementationQuery(context_name=context_name, name=name)
    result = _get_implementation(cmd)
    typer.echo(result.implementation.model_dump_json(indent=2))
