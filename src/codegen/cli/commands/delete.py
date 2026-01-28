from pathlib import Path

import typer
from codegen.cli.utils import get_container
from codegen.domain_definition.application.use_cases.modify_blueprint import (
    DeleteComponentCommand,
)

app = typer.Typer(name="delete", help="Delete components")


@app.command("context")
def delete_context(
    name: str = typer.Argument(..., help="Name of the Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    with get_container(config_file=config_file) as container:
        use_case = container.delete_component_use_case()
        cmd = DeleteComponentCommand(context="ROOT", name=name, type="context")
        use_case.execute(cmd)
    typer.echo(f"✅ Context '{name}' deleted.")


def _delete_component(name: str, context: str, type_: str, config_file: Path):
    with get_container(config_file=config_file) as container:
        use_case = container.delete_component_use_case()
        cmd = DeleteComponentCommand(context=context, name=name, type=type_)
        use_case.execute(cmd)
    typer.echo(f"✅ {type_.capitalize()} '{name}' deleted from context '{context}'.")


@app.command("aggregate")
def delete_aggregate(
    name: str = typer.Argument(..., help="Name of the Aggregate"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "aggregate", config_file)


@app.command("entity")
def delete_entity(
    name: str = typer.Argument(..., help="Name of the Entity"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "entity", config_file)


@app.command("value-object")
def delete_value_object(
    name: str = typer.Argument(..., help="Name of the Value Object"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "value_object", config_file)


@app.command("service")
def delete_service(
    name: str = typer.Argument(..., help="Name of the Service"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "service", config_file)


@app.command("enum")
def delete_enum(
    name: str = typer.Argument(..., help="Name of the Enum"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "enum", config_file)


@app.command("port")
def delete_port(
    name: str = typer.Argument(..., help="Name of the Port"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "port", config_file)
