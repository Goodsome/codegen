from pathlib import Path
from typing import Optional

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
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.enum_member_spec import EnumMemberSpec

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
    elif type_ == "implementation":
        found_component = next((x for x in ctx_obj.infrastructure.implementations if str(x.name) == name), None)
    elif type_ == "use_case":
        found_component = next((x for x in ctx_obj.application.use_cases if str(x.name) == name), None)
    
    if not found_component:
        typer.echo(f"❌ {type_.capitalize()} '{name}' not found inside context '{context}'.")
        raise typer.Exit(1)

    # 4. Modify
    new_desc = description if description is not None else found_component.description
    
    # Merge Attributes if applicable
    final_attrs = list(found_component.attributes) if hasattr(found_component, "attributes") else []
    
    if type_ == "use_case":
          # Use cases don't support generic attribute update here
          pass 
    elif attributes:
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
    elif type_ == "implementation":
        new_component = ImplementationSpec(
            name=found_component.name,
            description=new_desc,
            attributes=final_attrs,
            implements=found_component.implements,
            technology=found_component.technology,
            private_methods=found_component.private_methods
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


@app.command("implementation")
def update_implementation(
    name: str = typer.Argument(..., help="Name of the Implementation"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    attributes: list[str] = typer.Option(
        [], "--add-attr", "-a", help="Add attributes 'name:type'"
    ),
    tech: str = typer.Option(None, "--tech", "-t", help="New Technology"),
    implements: str = typer.Option(None, "--implements", "-i", help="New Interface implemented"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Update an Infrastructure Implementation."""
    with get_container(config_file=config_file) as container:
        # Custom logic for implementations because of fields like tech and implements
        
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
        found = next((x for x in ctx_obj.infrastructure.implementations if str(x.name) == name), None)
        
        if not found:
            typer.echo(f"❌ Implementation '{name}' not found inside context '{context}'.")
            raise typer.Exit(1)
            
        # 4. Modify
        new_desc = description if description is not None else found.description
        new_tech = SnakeString(tech) if tech else found.technology
        new_implements = implements if implements else found.implements
        
        # Merge Attributes
        final_attrs = list(found.attributes)
        if attributes:
            for attr_str in attributes:
                pa = AttributeParser.parse(attr_str)
                new_spec = AttributeSpec.create(name=pa.name, type=pa.type, optional=pa.optional)
                idx = next((i for i, x in enumerate(final_attrs) if x.name == new_spec.name), -1)
                if idx >= 0:
                    final_attrs[idx] = new_spec
                else:
                    final_attrs.append(new_spec)

        new_impl = ImplementationSpec(
            name=found.name,
            description=new_desc,
            technology=new_tech,
            implements=new_implements,
            attributes=final_attrs,
            private_methods=found.private_methods
        )
        
        # 5. Save
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=new_impl))
        typer.echo(f"✅ Implementation '{name}' updated.")


@app.command("use-case")
def update_use_case(
    name: str = typer.Argument(..., help="Name of the Use Case"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Update a Use Case."""
    with get_container(config_file=config_file) as container:
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
        found = next((x for x in ctx_obj.application.use_cases if str(x.name) == name), None)
        
        if not found:
            typer.echo(f"❌ Use Case '{name}' not found inside context '{context}'.")
            raise typer.Exit(1)
            
        # 4. Modify
        new_desc = description if description is not None else found.description
        
        new_uc = UseCaseSpec(
            name=found.name,
            kind=found.kind,
            description=new_desc,
            dependencies=found.dependencies,
            command=found.command,
            query=found.query,
            result=found.result
        )
        
        # 5. Save
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=new_uc))
        typer.echo(f"✅ Use Case '{name}' updated.")


@app.command("method")
def update_method(
    name: str = typer.Argument(..., help="Name of the Method"),
    on: str = typer.Option(..., "--on", help="Name of the parent component"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    type_: str = typer.Option(..., "--type", help="Type of parent component: service, aggregate, implementation, port"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Update a method description."""
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
        method_list = []
        
        # 3. Find Parent
        if type_ == "service":
            parent = next((x for x in ctx_obj.domain.services if str(x.name) == on), None)
            if parent: method_list = parent.operations
        elif type_ == "aggregate":
            parent = next((x for x in ctx_obj.domain.aggregates if str(x.name) == on), None)
            if parent: method_list = parent.behaviors
        elif type_ == "implementation":
            parent = next((x for x in ctx_obj.infrastructure.implementations if str(x.name) == on), None)
            if parent: method_list = parent.private_methods
        elif type_ == "port":
            parent = next((x for x in ctx_obj.domain.ports if str(x.name) == on), None)
            if not parent:
                parent = next((x for x in ctx_obj.application.ports if str(x.name) == on), None)
            if parent: method_list = parent.operations
        else:
            typer.echo(f"❌ Invalid type: {type_}")
            raise typer.Exit(1)
            
        if not parent:
            typer.echo(f"❌ {type_.capitalize()} '{on}' not found in context '{context}'.")
            raise typer.Exit(1)
            
        # 4. Find Method
        method = next((m for m in method_list if str(m.name) == name), None)
        if not method:
            typer.echo(f"❌ Method '{name}' not found in {type_} '{on}'.")
            raise typer.Exit(1)

        # 5. Modify
        new_desc = description if description is not None else method.description
        
        # TODO: Support updating args and return type? 
        # For now just description as per MVP 
        
        new_method = MethodSpec(
            name=method.name,
            inputs=method.inputs,
            output=method.output,
            description=new_desc
        )

        # 6. Save
        updated_component = None
        if type_ == "service":
            updated_component = parent.update_operation(new_method)
        elif type_ == "aggregate":
            updated_component = parent.update_behavior(new_method)
        elif type_ == "implementation":
            updated_component = parent.update_private_method(new_method)
        elif type_ == "port":
            updated_component = parent.update_operation(new_method)

        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=updated_component))
        
    typer.echo(f"✅ Method '{name}' updated in {type_} '{on}'.")


@app.command("member")
def update_member(
    name: str = typer.Argument(..., help="Name of the Enum Member"),
    on: str = typer.Option(..., "--on", help="Name of the Enum"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    value: str = typer.Option(None, "--value", help="New Value"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Update an Enum Member."""
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
            
        # 4. Find Member
        member = next((m for m in parent.members if str(m.name) == name), None)
        if not member:
            typer.echo(f"❌ Member '{name}' not found in Enum '{on}'.")
            raise typer.Exit(1)

        # 5. Modify
        new_desc = description if description is not None else member.description
        new_value = value if value is not None else member.value

        new_member = EnumMemberSpec(
            name=member.name,
            value=new_value,
            description=new_desc
        )

        # 6. Save
        updated_component = parent.update_member(new_member)
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=updated_component))
        
    typer.echo(f"✅ Member '{name}' updated in Enum '{on}'.")
