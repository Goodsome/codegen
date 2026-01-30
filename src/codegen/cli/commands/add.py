from pathlib import Path
from typing import Optional

import typer
from codegen.cli.utils import get_container
from codegen.domain_definition.application.use_cases.modify_blueprint import (
    AddComponentCommand,
    UpdateComponentCommand,
)
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprintCommand,
)
from codegen.shared.application.services.attribute_parser import AttributeParser
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.bounded_context import BoundedContext
from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.domain_definition.domain.value_objects.value_object_spec import ValueObjectSpec
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.enum_spec import EnumSpec
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.domain_definition.domain.enums import PortType, UseCaseKind
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.enum_member_spec import EnumMemberSpec
from codegen.shared.domain.value_objects.macro_string import MacroString

app = typer.Typer(name="add", help="Add components to the blueprint")


@app.command("context")
def add_context(
    name: str = typer.Argument(..., help="Name of the Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Bounded Context."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        context = BoundedContext.create(name=name, description=description)
        cmd = AddComponentCommand(context=name, component=context)
        use_case.execute(cmd)
    typer.echo(f"✅ Context '{name}' added.")


def _parse_attributes(attributes: list[str]) -> list[AttributeSpec]:
    parsed_attrs = []
    for attr_str in attributes:
        pa = AttributeParser.parse(attr_str)
        parsed_attrs.append(
            AttributeSpec.create(name=pa.name, type=pa.type, optional=pa.optional)
        )
    return parsed_attrs


@app.command("aggregate")
def add_aggregate(
    name: str = typer.Argument(..., help="Name of the Aggregate"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    attributes: list[str] = typer.Option(
        [], "--attr", "-a", help="Attributes in format 'name:type:optional'"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Aggregate."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        parsed_attrs = _parse_attributes(attributes)
        aggregate = AggregateSpec(
            name=name,  # type: ignore
            description=description,
            attributes=parsed_attrs,
        )
        cmd = AddComponentCommand(context=context, component=aggregate)
        use_case.execute(cmd)
    typer.echo(f"✅ Aggregate '{name}' added to context '{context}'.")


@app.command("entity")
def add_entity(
    name: str = typer.Argument(..., help="Name of the Entity"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    attributes: list[str] = typer.Option(
        [], "--attr", "-a", help="Attributes in format 'name:type:optional'"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Entity."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        parsed_attrs = _parse_attributes(attributes)
        entity = EntitySpec(
            name=name,  # type: ignore
            description=description,
            attributes=parsed_attrs,
        )
        cmd = AddComponentCommand(context=context, component=entity)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Entity '{name}' added to context '{context}'.")


@app.command("value-object")
def add_value_object(
    name: str = typer.Argument(..., help="Name of the Value Object"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    attributes: list[str] = typer.Option(
        [], "--attr", "-a", help="Attributes in format 'name:type:optional'"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Value Object."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        parsed_attrs = _parse_attributes(attributes)
        vo = ValueObjectSpec(
            name=name,  # type: ignore
            description=description,
            attributes=parsed_attrs,
        )
        cmd = AddComponentCommand(context=context, component=vo)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Value Object '{name}' added to context '{context}'.")


@app.command("service")
def add_service(
    name: str = typer.Argument(..., help="Name of the Service"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Domain Service."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        service = ServiceSpec(
            name=name,  # type: ignore
            description=description,
            operations=[], 
        )
        cmd = AddComponentCommand(context=context, component=service)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Service '{name}' added to context '{context}'.")


@app.command("enum")
def add_enum(
    name: str = typer.Argument(..., help="Name of the Enum"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    # TODO: Support adding members
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Enum."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        enum_ = EnumSpec(
            name=name, # type: ignore
            description=description,
            members=[]
        )
        cmd = AddComponentCommand(context=context, component=enum_)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Enum '{name}' added to context '{context}'.")


@app.command("port")
def add_port(
    name: str = typer.Argument(..., help="Name of the Port"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    kind: str = typer.Option(..., "--kind", "-k", help="Port Type: repository, client, provider, adapter"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    aggregate: str = typer.Option(None, "--aggregate", "-agg", help="Related Aggregate (required for repositories)"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Port."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        
        try:
            port_kind = PortType(kind.lower())
        except ValueError:
            typer.echo(f"❌ Invalid port kind: {kind}. Valid values: {[e.value for e in PortType]}")
            raise typer.Exit(1)

        port = PortSpec.create(
            name=name,
            kind=port_kind,
            description=description,
            aggregate=aggregate
        )
        
        cmd = AddComponentCommand(context=context, component=port)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Port '{name}' ({kind}) added to context '{context}'.")


@app.command("implementation")
def add_implementation(
    name: str = typer.Argument(..., help="Name of the Implementation"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    tech: str = typer.Option(..., "--tech", "-t", help="Technology/Library (e.g. sqlalchemy)"),
    implements: str = typer.Option(..., "--implements", "-i", help="Interface name implemented by this component"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    attributes: list[str] = typer.Option(
        [], "--attr", "-a", help="Attributes in format 'name:type:optional'"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Infrastructure Implementation."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        parsed_attrs = _parse_attributes(attributes)
        
        impl = ImplementationSpec.create(
            name=name,
            technology=tech,
            implements=implements,
            description=description,
            attributes=parsed_attrs,
        )
        
        cmd = AddComponentCommand(context=context, component=impl)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Implementation '{name}' (using {tech}) added to context '{context}'.")


@app.command("use-case")
def add_use_case(
    name: str = typer.Argument(..., help="Name of the Use Case"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    kind: str = typer.Option(..., "--kind", "-k", help="Use Case Type: command, query"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a new Use Case."""
    with get_container(config_file=config_file) as container:
        use_case = container.add_component_use_case()
        
        try:
            uc_kind = UseCaseKind(kind.lower())
        except ValueError:
            typer.echo(f"❌ Invalid use case kind: {kind}. Valid values: {[e.value for e in UseCaseKind]}")
            raise typer.Exit(1)

        uc = UseCaseSpec.create(
            name=name,
            kind=uc_kind,
            description=description,
        )
        
        cmd = AddComponentCommand(context=context, component=uc)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Use Case '{name}' ({kind}) added to context '{context}'.")


@app.command("method")
def add_method(
    name: str = typer.Argument(..., help="Name of the Method"),
    on: str = typer.Option(..., "--on", help="Name of the parent component (Service, Aggregate, Implementation, Port)"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    type_: str = typer.Option(..., "--type", help="Type of parent component: service, aggregate, implementation, port"),
    args: list[str] = typer.Option([], "--arg", help="Arguments in format 'name:type:optional'"),
    ret: str = typer.Option("None", "--return", "--ret", help="Return type"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a method to a Service, Aggregate, Implementation, or Port."""
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

        # 3. Helpers
        parsed_args = _parse_attributes(args)
        method_spec = MethodSpec.create(
            name=name,
            inputs=parsed_args,
            output=MethodOutput(type=ret)
        )
        method_spec = method_spec.model_copy(update={"description": description})

        # 4. Find Parent and Add Method
        updated_component = None
        type_ = type_.lower()

        if type_ == "service":
            parent = next((x for x in ctx_obj.domain.services if str(x.name) == on), None)
            if not parent:
                typer.echo(f"❌ Service '{on}' not found in context '{context}'.")
                raise typer.Exit(1)
            updated_component = parent.add_operation(method_spec)

        elif type_ == "aggregate":
            parent = next((x for x in ctx_obj.domain.aggregates if str(x.name) == on), None)
            if not parent:
                typer.echo(f"❌ Aggregate '{on}' not found in context '{context}'.")
                raise typer.Exit(1)
            updated_component = parent.add_behavior(method_spec)

        elif type_ == "implementation":
            parent = next((x for x in ctx_obj.infrastructure.implementations if str(x.name) == on), None)
            if not parent:
                typer.echo(f"❌ Implementation '{on}' not found in context '{context}'.")
                raise typer.Exit(1)
            updated_component = parent.add_private_method(method_spec)
            
        elif type_ == "port":
            parent = next((x for x in ctx_obj.domain.ports if str(x.name) == on), None)
            if not parent:
                # Try application ports if not in domain
                parent = next((x for x in ctx_obj.application.ports if str(x.name) == on), None)
            
            if not parent:
                typer.echo(f"❌ Port '{on}' not found in context '{context}'.")
                raise typer.Exit(1)
            updated_component = parent.add_operation(method_spec)

        else:
            typer.echo(f"❌ Invalid type: {type_}. Valid values: service, aggregate, implementation, port")
            raise typer.Exit(1)

        # 5. Save
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=updated_component))
        
    typer.echo(f"✅ Method '{name}' added to {type_} '{on}'.")


@app.command("member")
def add_member(
    name: str = typer.Argument(..., help="Name of the Enum Member"),
    on: str = typer.Option(..., "--on", help="Name of the Enum"),
    context: str = typer.Option(..., "--context", help="Target Bounded Context"),
    value: str = typer.Option(None, "--value", help="Value of the member (optional)"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    """Add a member to an Enum."""
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

        # 4. Create Member
        member_spec = EnumMemberSpec(
            name=MacroString(name),
            value=value,
            description=description
        )

        # 5. Add Member
        updated_component = parent.add_member(member_spec)

        # 6. Save
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=updated_component))
        
    typer.echo(f"✅ Member '{name}' added to Enum '{on}'.")
