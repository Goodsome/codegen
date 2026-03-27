"""
Upsert Context command - Create or update a bounded context in the blueprint.
"""
import typer
from codegen.domain_definition.application.use_cases.upsert_context import (
    UpsertContext,
    UpsertContextCommand,
    UpsertContextResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _upsert_context(
    cmd: UpsertContextCommand,
    use_case: UpsertContext = Provide["domain_definition_container.upsert_context"],
) -> UpsertContextResult:
    return use_case.execute(cmd)


def upsert_context(
    name: Annotated[str, typer.Argument(
        ...,
        help="Context name (e.g., 'Billing', 'OrderManagement')",
    )],
    description: Annotated[str, typer.Option(
        "--description", "-d", help="Context description"
    )] = "",
) -> None:
    """
    Upsert Context: Create or update a bounded context in the blueprint.

    If a context with the given name already exists, its description will be updated.
    If no context with the given name exists, a new one will be created.

    Examples:
        $ codegen upsert-context Billing --description "Payment processing"
        $ codegen upsert-context "OrderManagement" -d "Order and fulfillment management"
    """
    cmd = UpsertContextCommand(name=name, description=description)
    _upsert_context(cmd)
    typer.echo(f"Upserted context '{name}'")
