"""
Schema command - Generate JSON schema for blueprint validation.
"""
import typer
from dependency_injector.wiring import Provide, inject
from codegen.python_gen.application.use_cases.generate_schema_json import (
    GenerateSchemaJson,
    GenerateSchemaJsonCommand,
)


@inject
def _generate_schema_json(
    cmd: GenerateSchemaJsonCommand,
    use_case: GenerateSchemaJson = Provide[
        "python_gen_container.generate_schema_json"
    ],
) -> None:
    return use_case.execute(cmd)


def schema() -> None:
    """
    Schema: Output JSON schema for the blueprint.

    Generates a JSON schema file that can be used for IDE autocompletion
    and validation of codegen.yaml files.

    Examples:
        $ codegen schema
    """
    cmd = GenerateSchemaJsonCommand()
    _generate_schema_json(cmd)
    typer.echo("Schema generated successfully.")
