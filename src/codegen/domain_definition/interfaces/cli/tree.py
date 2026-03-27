"""
Tree command - Display blueprint structure as a visual tree.
"""
from typing import Optional, Any

import typer
from rich.tree import Tree
from rich.console import Console
from pydantic import BaseModel
from dependency_injector.wiring import Provide, inject
from typing import Annotated

from codegen.domain_definition.application.use_cases.get_value import (
    GetValue,
    GetValueCommand,
)
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)

# Icon mappings for different DDD concepts
ICONS = {
    # Top level
    "Blueprint": "📦",
    "Project": "📦",
    # Context
    "BoundedContext": "📂",
    "Context": "📂",
    # Domain layer
    "Aggregate": "🔷",
    "AggregateSpec": "🔷",
    "Entity": "🔸",
    "EntitySpec": "🔸",
    "ValueObject": "💎",
    "ValueObjectSpec": "💎",
    "Service": "🔧",
    "ServiceSpec": "🔧",
    "Enum": "📊",
    "EnumSpec": "📊",
    "Port": "🔌",
    "PortSpec": "🔌",
    # Application layer
    "UseCase": "⚡",
    "UseCaseSpec": "⚡",
    # Infrastructure layer
    "Implementation": "🏗️",
    "ImplementationSpec": "🏗️",
    # Methods and members
    "Method": "🟢",
    "MethodSpec": "🟢",
    "Member": "📍",
    "Attribute": "📝",
    # Default
    "default": "📄",
}


def get_icon(type_name: str) -> str:
    """Get icon for a type name."""
    return ICONS.get(type_name, ICONS["default"])


def get_display_name(obj: Any) -> str:
    """Get display name from an object."""
    if hasattr(obj, 'name'):
        return str(obj.name)
    return obj.__class__.__name__


def get_type_name(obj: Any) -> str:
    """Get type name from an object."""
    return obj.__class__.__name__


def build_tree_node(
    obj: Any,
    tree: Tree,
    current_depth: int,
    max_depth: int,
    show_detail: bool,
) -> None:
    """Recursively build tree nodes from a Pydantic model or list."""
    if max_depth != -1 and current_depth >= max_depth:
        return

    if isinstance(obj, list):
        for item in obj:
            add_item_to_tree(item, tree, current_depth, max_depth, show_detail)
    elif isinstance(obj, BaseModel):
        add_model_children(obj, tree, current_depth, max_depth, show_detail)


def add_item_to_tree(
    item: Any,
    tree: Tree,
    current_depth: int,
    max_depth: int,
    show_detail: bool,
) -> None:
    """Add a single item to the tree."""
    if not isinstance(item, BaseModel):
        tree.add(f"[dim]{item}[/dim]")
        return

    type_name = get_type_name(item)
    name = get_display_name(item)
    icon = get_icon(type_name)

    label = f"{icon} [bold cyan]{name}[/bold cyan]"
    if show_detail and hasattr(item, 'description') and item.description:
        desc = str(item.description)[:40]
        if len(str(item.description)) > 40:
            desc += "..."
        label += f" [dim]({desc})[/dim]"

    branch = tree.add(label)
    add_model_children(item, branch, current_depth + 1, max_depth, show_detail)


def add_model_children(
    model: BaseModel,
    tree: Tree,
    current_depth: int,
    max_depth: int,
    show_detail: bool,
) -> None:
    """Add children of a Pydantic model to the tree."""
    if max_depth != -1 and current_depth >= max_depth:
        return

    traversable_fields = get_traversable_fields(model, show_detail)

    for field_name in traversable_fields:
        if not hasattr(model, field_name):
            continue

        value = getattr(model, field_name)

        if value is None:
            continue

        if isinstance(value, list) and value:
            section_icon = get_section_icon(field_name)
            section = tree.add(f"{section_icon} [bold]{field_name}[/bold] ({len(value)})")
            for item in value:
                add_item_to_tree(item, section, current_depth + 1, max_depth, show_detail)
        elif isinstance(value, BaseModel) and not is_simple_value_object(value):
            section_icon = get_section_icon(field_name)
            section = tree.add(f"{section_icon} [bold]{field_name}[/bold]")
            add_model_children(value, section, current_depth + 1, max_depth, show_detail)


def get_traversable_fields(model: BaseModel, show_detail: bool) -> list[str]:
    """Get list of fields that should be traversed for tree display."""
    type_name = get_type_name(model)

    field_map = {
        "Blueprint": ["contexts"],
        "BoundedContext": ["domain", "application", "infrastructure"],
        "DomainSpec": ["enums", "aggregates", "entities", "value_objects", "services", "ports"],
        "ApplicationSpec": ["use_cases", "ports", "services"],
        "MetaApplication": ["use_cases", "ports", "services"],
        "InfrastructureSpec": ["implementations"],
        "MetaInfrastructure": ["implementations"],
    }

    detail_field_map = {
        "AggregateSpec": ["attributes"],
        "EntitySpec": ["attributes"],
        "ValueObjectSpec": ["attributes"],
    }

    if show_detail:
        field_map.update(detail_field_map)

    return field_map.get(type_name, [])


def get_section_icon(field_name: str) -> str:
    """Get icon for a section/field name."""
    icons = {
        "contexts": "📂",
        "domain": "🏛️",
        "application": "⚙️",
        "infrastructure": "🏗️",
        "aggregates": "🔷",
        "entities": "🔸",
        "value_objects": "💎",
        "services": "🛠️",
        "enums": "📊",
        "ports": "🔌",
        "use_cases": "⚡",
        "implementations": "🏗️",
    }
    return icons.get(field_name, "")


def is_simple_value_object(obj: BaseModel) -> bool:
    """Check if an object is a simple value object that shouldn't be expanded."""
    simple_types = {"MacroString", "PascalString", "SnakeString", "Attribute", "MethodOutput"}
    return get_type_name(obj) in simple_types


@inject
def _load_blueprint(
    cmd: LoadBlueprintCommand,
    use_case: LoadBlueprint = Provide["domain_definition_container.load_blueprint"],
) -> Any:
    return use_case.execute(cmd)


@inject
def _get_value(
    cmd: GetValueCommand,
    use_case: GetValue = Provide["domain_definition_container.get_value"],
) -> Any:
    return use_case.execute(cmd)


def tree(
    path: Annotated[Optional[str], typer.Argument(
        help="Optional path to start from (e.g., 'contexts.DomainDefinition')",
    )] = None,
    depth: Annotated[int, typer.Option("--depth", "-d")] = -1,
    detail: Annotated[bool, typer.Option("--detail/--no-detail")] = False,
) -> None:
    """
    Tree: Display blueprint structure as a visual tree.

    Provides a hierarchical overview of your project's DDD structure,
    making it easy to understand the organization of contexts,
    aggregates, entities, and other components.

    Examples:
        $ codegen tree
        $ codegen tree --depth 2
        $ codegen tree contexts.DomainDefinition
        $ codegen tree --detail
    """
    console = Console()

    try:
        result = _load_blueprint(LoadBlueprintCommand())

        if not result or not result.blueprint:
            console.print("[red]Error: Blueprint not found[/red]")
            raise typer.Exit(1)

        blueprint = result.blueprint

        target = blueprint
        root_label = f"📦 [bold]Project: {blueprint.name}[/bold]"

        if path:
            target = _get_value(GetValueCommand(path=path))
            root_label = f"📍 [bold]{path}[/bold]"

        root = Tree(root_label)

        if isinstance(target, list):
            for item in target:
                add_item_to_tree(item, root, 0, depth, detail)
        elif isinstance(target, BaseModel):
            add_model_children(target, root, 0, depth, detail)
        else:
            root.add(f"[dim]{target}[/dim]")

        console.print(root)

    except KeyError as e:
        console.print(f"[red]Error: Path not found - {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
