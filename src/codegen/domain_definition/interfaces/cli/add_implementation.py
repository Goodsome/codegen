"""
AddImplementation command - Add a new implementation to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_implementation import (
    AddImplementation,
    AddImplementationCommand,
    AddImplementationResult,
)


@inject
def _add_implementation(
    cmd: AddImplementationCommand,
    use_case: AddImplementation = Provide[
        "domain_definition_container.add_implementation"
    ],
) -> AddImplementationResult:
    return use_case.execute(cmd)


def add_implementation(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Implementation name")],
    implements: Annotated[str, typer.Argument(help="What this implementation implements")],
    technology: Annotated[str, typer.Argument(help="Technology used (e.g., Python, TypeScript)")],
    description: Annotated[str, typer.Argument(help="Implementation description")],
) -> None:
    """
    Add a new implementation to a bounded context.

    Examples:
        $ codegen infrastructure add-implementation Sales postgres "IDomainPort" "PostgreSQL implementation"
        $ codegen infrastructure add-implementation Billing stripe "IPaymentGateway" "Stripe payment gateway"
    """
    cmd = AddImplementationCommand(
        context_name=context_name,
        name=name,
        implements=implements,
        technology=technology,
        description=description,
    )
    result = _add_implementation(cmd)
    if result.success:
        typer.echo(f"Successfully added implementation '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add implementation '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
