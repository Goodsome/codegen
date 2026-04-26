"""UpdateDomainException command - Update an existing domain exception in a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_domain_exception import (
    UpdateDomainException,
    UpdateDomainExceptionCommand,
    UpdateDomainExceptionResult,
)


@inject
def _update_domain_exception(
    cmd: UpdateDomainExceptionCommand,
    use_case: UpdateDomainException = Provide[
        "domain_definition_container.update_domain_exception"
    ],
) -> UpdateDomainExceptionResult:
    return use_case.execute(cmd)


def update_domain_exception(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain exception name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing domain exception in a bounded context.
    """
    cmd = UpdateDomainExceptionCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_domain_exception(cmd)
    if result.success:
        typer.echo(f"Successfully updated domain exception '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update domain exception '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
