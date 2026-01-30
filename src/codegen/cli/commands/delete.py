from pathlib import Path

import typer
from codegen.cli.utils import get_container
from codegen.domain_definition.application.use_cases.modify_blueprint import (
    DeleteComponentCommand,
    UpdateComponentCommand
)
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprintCommand,
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


@app.command("implementation")
def delete_implementation(
    name: str = typer.Argument(..., help="Name of the Implementation"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "implementation", config_file)


@app.command("use-case")
def delete_use_case(
    name: str = typer.Argument(..., help="Name of the Use Case"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    _delete_component(name, context, "use_case", config_file)


@app.command("method")
def delete_method(
    name: str = typer.Argument(..., help="Name of the Method"),
    on: str = typer.Option(..., "--on", help="Name of the parent component"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    type_: str = typer.Option(..., "--type", help="Type of parent component: service, aggregate, implementation, port"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Delete a method from a Service, Aggregate, Implementation, or Port."""
    with get_container(config_file=config_file) as container:
        # 1. Load Blueprint
        loader = container.load_blueprint_use_case()
        res = loader.execute(LoadBlueprintCommand())
        blueprint = res.blueprint

        # 2. Find Context
        ctx_obj = blueprint.get_context(context)
        if not ctx_obj:
            typer.echo(f"❌ Context '{context}' not found.")
            raise typer.Exit(1)
            
        type_ = type_.lower()
        parent = None
        
        # 3. Find Parent
        if type_ == "service":
            parent = next((x for x in ctx_obj.domain.services if str(x.name) == on), None)
        elif type_ == "aggregate":
            parent = next((x for x in ctx_obj.domain.aggregates if str(x.name) == on), None)
        elif type_ == "implementation":
            parent = next((x for x in ctx_obj.infrastructure.implementations if str(x.name) == on), None)
        elif type_ == "port":
            parent = next((x for x in ctx_obj.domain.ports if str(x.name) == on), None)
            if not parent:
                parent = next((x for x in ctx_obj.application.ports if str(x.name) == on), None)
        else:
            typer.echo(f"❌ Invalid type: {type_}")
            raise typer.Exit(1)
            
        if not parent:
            typer.echo(f"❌ {type_.capitalize()} '{on}' not found in context '{context}'.")
            raise typer.Exit(1)

        # 4. Delete Method
        updated_component = None
        try:
            if type_ == "service":
                updated_component = parent.delete_operation(name)
            elif type_ == "aggregate":
                updated_component = parent.delete_behavior(name)
            elif type_ == "implementation":
                updated_component = parent.delete_private_method(name)
            elif type_ == "port":
                updated_component = parent.delete_operation(name)
        except ValueError as e:
            typer.echo(f"❌ {e}")
            raise typer.Exit(1)

        # 5. Save
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=updated_component))
        
    typer.echo(f"✅ Method '{name}' deleted from {type_} '{on}'.")


@app.command("member")
def delete_member(
    name: str = typer.Argument(..., help="Name of the Enum Member"),
    on: str = typer.Option(..., "--on", help="Name of the Enum"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Delete a member from an Enum."""
    with get_container(config_file=config_file) as container:
        # 1. Load Blueprint
        loader = container.load_blueprint_use_case()
        res = loader.execute(LoadBlueprintCommand())
        blueprint = res.blueprint

        # 2. Find Context
        ctx_obj = blueprint.get_context(context)
        if not ctx_obj:
            typer.echo(f"❌ Context '{context}' not found.")
            raise typer.Exit(1)

        # 3. Find Enum
        parent = next((x for x in ctx_obj.domain.enums if str(x.name) == on), None)
        if not parent:
            typer.echo(f"❌ Enum '{on}' not found in context '{context}'.")
            raise typer.Exit(1)

        # 4. Delete Member
        try:
            updated_component = parent.delete_member(name)
        except ValueError as e:
            typer.echo(f"❌ {e}")
            raise typer.Exit(1)

        # 5. Save
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=updated_component))
        
    typer.echo(f"✅ Member '{name}' deleted from Enum '{on}'.")
