"""
Tree command - Display blueprint structure as a visual tree.
"""
from typing import Any

import typer
from rich.tree import Tree
from rich.console import Console
from pydantic import BaseModel
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)

# Icon mappings for different DDD concepts
ICONS = {
    "Blueprint": "📦",
    "Project": "📦",
    "BoundedContext": "📂",
    "Context": "📂",
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
    "UseCase": "⚡",
    "UseCaseSpec": "⚡",
    "Implementation": "🏗️",
    "ImplementationSpec": "🏗️",
    "default": "📄",
}

# Icon mappings for section/field names
SECTION_ICONS = {
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


def get_icon(type_name: str) -> str:
    """Get icon for a type name."""
    return ICONS.get(type_name, ICONS["default"])


def get_section_icon(field_name: str) -> str:
    """Get icon for a section/field name."""
    return SECTION_ICONS.get(field_name, "")


def get_display_name(obj: Any) -> str:
    """Get display name from an object."""
    if hasattr(obj, 'name'):
        return str(obj.name)
    return obj.__class__.__name__


def get_type_name(obj: Any) -> str:
    """Get type name from an object."""
    return obj.__class__.__name__


def add_leaf_item(item: BaseModel, tree: Tree) -> None:
    """Add a leaf item (like EnumSpec, ValueObjectSpec) to the tree."""
    type_name = get_type_name(item)
    name = get_display_name(item)
    icon = get_icon(type_name)
    tree.add(f"{icon} [bold cyan]{name}[/bold cyan]")


def add_section_with_items(
    parent_tree: Tree,
    field_name: str,
    items: list,
    branch: bool = False,
) -> None:
    """Add a section node with its items (e.g., enums with their individual items)."""
    if not items:
        return

    section_icon = get_section_icon(field_name)
    section = parent_tree.add(f"{section_icon} [bold]{field_name}[/bold] ({len(items)})")

    for item in items:
        if isinstance(item, BaseModel):
            if branch:
                # For items like BoundedContext that have their own children
                item_name = get_display_name(item)
                item_icon = get_icon(get_type_name(item))
                item_branch = section.add(f"{item_icon} [bold cyan]{item_name}[/bold cyan]")
                add_model_children(item, item_branch)
            else:
                add_leaf_item(item, section)
        else:
            section.add(f"[dim]{item}[/dim]")


def add_model_children(model: BaseModel, tree: Tree) -> None:
    """Add children of a Pydantic model to the tree based on its type."""
    type_name = get_type_name(model)

    if type_name == "Blueprint":
        add_section_with_items(tree, "contexts", model.contexts, branch=True)

    elif type_name == "BoundedContext":
        if hasattr(model, 'domain') and model.domain:
            domain_tree = tree.add(f"{get_section_icon('domain')} [bold]domain[/bold]")
            add_model_children(model.domain, domain_tree)
        if hasattr(model, 'application') and model.application:
            app_tree = tree.add(f"{get_section_icon('application')} [bold]application[/bold]")
            add_model_children(model.application, app_tree)
        if hasattr(model, 'infrastructure') and model.infrastructure:
            infra_tree = tree.add(f"{get_section_icon('infrastructure')} [bold]infrastructure[/bold]")
            add_model_children(model.infrastructure, infra_tree)

    elif type_name == "DomainSpec":
        add_section_with_items(tree, "enums", model.enums)
        add_section_with_items(tree, "aggregates", model.aggregates)
        add_section_with_items(tree, "entities", model.entities)
        add_section_with_items(tree, "value_objects", model.value_objects)
        add_section_with_items(tree, "services", model.services)
        add_section_with_items(tree, "ports", model.ports)

    elif type_name == "ApplicationSpec":
        add_section_with_items(tree, "use_cases", model.use_cases)
        add_section_with_items(tree, "ports", model.ports)
        add_section_with_items(tree, "services", model.services)

    elif type_name == "MetaApplication":
        add_section_with_items(tree, "use_cases", model.use_cases)
        add_section_with_items(tree, "ports", model.ports)
        add_section_with_items(tree, "services", model.services)

    elif type_name == "InfrastructureSpec":
        add_section_with_items(tree, "implementations", model.implementations)

    elif type_name == "MetaInfrastructure":
        add_section_with_items(tree, "implementations", model.implementations)


@inject
def _load_blueprint(
    cmd: LoadBlueprintCommand,
    use_case: LoadBlueprint = Provide["domain_definition_container.load_blueprint"],
) -> Any:
    return use_case.execute(cmd)


def tree() -> None:
    """
    Tree: Display blueprint structure as a visual tree.

    Provides a hierarchical overview of your project's DDD structure,
    making it easy to understand the organization of contexts,
    aggregates, entities, and other components.

    Example:
        $ codegen tree
    """
    console = Console()

    try:
        result = _load_blueprint(LoadBlueprintCommand())

        if not result or not result.blueprint:
            console.print("[red]Error: Blueprint not found[/red]")
            raise typer.Exit(1)

        blueprint = result.blueprint

        root = Tree(f"📦 [bold]Project: {blueprint.name}[/bold]")
        add_model_children(blueprint, root)

        console.print(root)

    except KeyError as e:
        console.print(f"[red]Error: Path not found - {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
