"""
AddMethod command - Add a method (behavior, operation, private) to an element.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_method import (
    AddMethod,
    AddMethodCommand,
    AddMethodResult,
)
from codegen.domain_definition.domain.enums import ElementType, MethodKind


@inject
def _add_method(
    cmd: AddMethodCommand,
    use_case: AddMethod = Provide["domain_definition_container.add_method"],
) -> AddMethodResult:
    return use_case.execute(cmd)


def add_method(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    element_type: Annotated[ElementType, typer.Argument(help="Element type")],
    element_name: Annotated[str, typer.Argument(help="Element name")],
    method_kind: Annotated[MethodKind, typer.Argument(help="Method kind")],
    name: Annotated[str, typer.Argument(help="Method name")],
    description: Annotated[str, typer.Argument()],
    output_type: Annotated[str, typer.Argument(help="Output type")],
    inputs: Annotated[str | None, typer.Option("--inputs", "-i", help="JSON string of inputs list")] = None,
    rules: Annotated[str | None, typer.Option("--rules", "-r", help="JSON string of rules list")] = None,
    output_optional: Annotated[bool, typer.Option("--output-optional")] = False,
) -> None:
    """
    Add a method to an element.

    Examples:
        $ codegen field add-method sales entity behavior Order calculate_total float --inputs '[{"name": "discount", "type": "float", "optional": true}]'
    """
    import json

    parsed_inputs = []
    if inputs:
        parsed_inputs = json.loads(inputs)

    parsed_rules = []
    if rules:
        parsed_rules = json.loads(rules)

    cmd = AddMethodCommand(
        context_name=context_name,
        element_type=element_type,
        method_kind=method_kind,
        element_name=element_name,
        name=name,
        description=description,
        inputs=parsed_inputs,
        rules=parsed_rules,
        output_type=output_type,
        output_optional=output_optional,
    )
    result = _add_method(cmd)
    if result.success:
        typer.echo(f"Successfully added {method_kind.value} '{name}' to {element_type.value} '{element_name}'")
    else:
        typer.echo(f"Failed to add {method_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
