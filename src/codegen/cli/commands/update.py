from pathlib import Path

import typer
from codegen.cli.utils import get_container
from codegen.domain_definition.application.use_cases.modify_blueprint import (
    UpdateComponentCommand,
)
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprintCommand,
)
from codegen.shared.application.services.attribute_parser import AttributeParser
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.domain_definition.domain.value_objects.value_object_spec import ValueObjectSpec
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.domain_definition.domain.enums import PortType

app = typer.Typer(name="update", help="Update existing components")


def _update_attributes_and_desc(
    container, context: str, name: str, description: str | None, attributes: list[str], type_: str
):
    # 1. Load existing blueprint
    loader = container.load_blueprint_use_case()
    res = loader.execute(LoadBlueprintCommand())
    blueprint = res.blueprint

    # 2. Find Context
    ctx_obj = blueprint.get_context(context)
    if not ctx_obj:
        typer.echo(f"❌ Context '{context}' not found.")
        raise typer.Exit(1)

    # 3. Find Component
    found_component = None
    if type_ == "aggregate":
        found_component = next((x for x in ctx_obj.domain.aggregates if str(x.name) == name), None)
    elif type_ == "entity":
        found_component = next((x for x in ctx_obj.domain.entities if str(x.name) == name), None)
    elif type_ == "value_object":
        found_component = next((x for x in ctx_obj.domain.value_objects if str(x.name) == name), None)
    
    if not found_component:
        typer.echo(f"❌ {type_.capitalize()} '{name}' not found inside context '{context}'.")
        raise typer.Exit(1)

    # 4. Modify
    new_desc = description if description is not None else found_component.description
    
    # Merge Attributes if applicable
    final_attrs = list(found_component.attributes)
    if attributes:
        for attr_str in attributes:
            pa = AttributeParser.parse(attr_str)
            new_spec = AttributeSpec.create(name=pa.name, type=pa.type, optional=pa.optional)
            
            # Check existance
            idx = next((i for i, x in enumerate(final_attrs) if x.name == new_spec.name), -1)
            if idx >= 0:
                final_attrs[idx] = new_spec # Update
            else:
                final_attrs.append(new_spec) # Add

    # Create New Instance
    if type_ == "aggregate":
        new_component = AggregateSpec(
            name=found_component.name,
            description=new_desc,
            attributes=final_attrs,
            behaviors=found_component.behaviors
        )
    elif type_ == "entity":
        new_component = EntitySpec(
            name=found_component.name,
            description=new_desc,
            attributes=final_attrs,
        )
    elif type_ == "value_object":
        new_component = ValueObjectSpec(
            name=found_component.name,
            description=new_desc,
            attributes=final_attrs,
        )
    else:
        raise NotImplementedError(f"Update not implemented for {type_}")

    # 5. Save (Update)
    updater = container.update_component_use_case()
    updater.execute(UpdateComponentCommand(context=context, component=new_component))
    typer.echo(f"✅ {type_.capitalize()} '{name}' updated.")


@app.command("aggregate")
def update_aggregate(
    name: str = typer.Argument(..., help="Name of the Aggregate"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    attributes: list[str] = typer.Option(
        [], "--add-attr", "-a", help="Add attributes 'name:type'"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    with get_container(config_file=config_file) as container:
        _update_attributes_and_desc(container, context, name, description, attributes, "aggregate")


@app.command("entity")
def update_entity(
    name: str = typer.Argument(..., help="Name of the Entity"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    attributes: list[str] = typer.Option(
        [], "--add-attr", "-a", help="Add attributes 'name:type'"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    with get_container(config_file=config_file) as container:
        _update_attributes_and_desc(container, context, name, description, attributes, "entity")


@app.command("value-object")
def update_value_object(
    name: str = typer.Argument(..., help="Name of the Value Object"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    attributes: list[str] = typer.Option(
        [], "--add-attr", "-a", help="Add attributes 'name:type'"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    with get_container(config_file=config_file) as container:
        _update_attributes_and_desc(container, context, name, description, attributes, "value_object")


@app.command("port")
def update_port(
    name: str = typer.Argument(..., help="Name of the Port"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    kind: str = typer.Option(None, "--kind", "-k", help="New Port Type"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    with get_container(config_file=config_file) as container:
        # Custom logic for ports because they can be in two places and have 'kind'
        
        # 1. Load existing blueprint
        loader = container.load_blueprint_use_case()
        res = loader.execute(LoadBlueprintCommand())
        blueprint = res.blueprint

        # 2. Find Context
        ctx_obj = blueprint.get_context(context)
        if not ctx_obj:
            typer.echo(f"❌ Context '{context}' not found.")
            raise typer.Exit(1)

        # 3. Find Component (Domain or Application)
        found_port = next((p for p in ctx_obj.domain.ports if str(p.name) == name), None)
        if not found_port:
             found_port = next((p for p in ctx_obj.application.ports if str(p.name) == name), None)
        
        if not found_port:
            typer.echo(f"❌ Port '{name}' not found inside context '{context}'.")
            raise typer.Exit(1)
        
        # 4. Modify
        new_desc = description if description is not None else found_port.description
        new_kind = found_port.kind
        if kind:
            try:
                new_kind = PortType(kind.lower())
            except ValueError:
                typer.echo(f"❌ Invalid port kind: {kind}. Valid values: {[e.value for e in PortType]}")
                raise typer.Exit(1)

        new_port = PortSpec(
            name=found_port.name,
            kind=new_kind,
            description=new_desc,
            aggregate=found_port.aggregate,
            operations=found_port.operations
        )

        # 5. Save (Update)
        # UpdateComponentCommand will try domain then application update automatically
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=new_port))
        typer.echo(f"✅ Port '{name}' updated.")
