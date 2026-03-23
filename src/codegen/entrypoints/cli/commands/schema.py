"""
Schema command - Generate JSON schema for blueprint validation.

Replaces the old 'codegen generate-blueprint-schema' command.
"""

import typer
from codegen.entrypoints.cli.utils import get_container
from codegen.python_gen.application.use_cases.generate_schema_json import (
    GenerateSchemaJson,
    GenerateSchemaJsonCommand,
)

app = typer.Typer(name="schema", help="Generate blueprint JSON schema")


@app.command()
def schema():
    """
    Schema: Output JSON schema for the blueprint.
    
    Generates a JSON schema file that can be used for IDE autocompletion
    and validation of codegen.yaml files.
    
    Examples:
        $ codegen schema
    """
    with get_container() as container:
        use_case = GenerateSchemaJson(file_system_port=container.project_root_file_port())
        cmd = GenerateSchemaJsonCommand()
        use_case.execute(cmd)
        typer.echo("Schema generated successfully.")
