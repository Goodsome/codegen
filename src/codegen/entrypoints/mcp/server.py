"""
Codegen MCP Server.

Exposes codegen CLI commands as MCP tools for LLM integration via Model Context Protocol.
Uses FastMCP for simplified server implementation.

Available tools:
- build: Compile codegen.yaml into Python code
- reverse: Reverse-engineer Python code into codegen.yaml
- tree: Display blueprint structure as text tree
- get: Query a value from blueprint by path
- set: Set or update a value in blueprint by path
- rm: Remove a value from blueprint by path
"""

import json
from pathlib import Path
from typing import Any
from importlib import resources

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from codegen.bootstrap import Container
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprintCommand,
)
from codegen.domain_definition.application.use_cases.get_value import (
    GetValueCommand,
)
from codegen.domain_definition.application.use_cases.set_value import SetValueCommand
from codegen.domain_definition.application.use_cases.remove_value import RemoveValueCommand
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprintCommand,
)
from codegen.orchestration.domain.value_objects.build_result import BuildResult

# Create MCP server instance
mcp = FastMCP("Codegen MCP Server")


def _get_container(
        config_file: Path,
        root_path: Path,
        output: str = "src",
) -> Container:
    """Create a configured container instance using a specific root path.

    Args:
        config_file: Path to codegen.yaml (relative or absolute)
        root_path: Project root directory
        output: Output directory - "src" (default) or custom path
    """
    cwd = root_path

    yaml_path = config_file if config_file.is_absolute() else (cwd / config_file)

    # Resolve output directory
    if output == "src":
        output_dir = cwd / "src"
    else:
        output_path = Path(output)
        output_dir = output_path if output_path.is_absolute() else (cwd / output_path)

    template_root = resources.files("codegen") / "python_gen" / "templates"

    with resources.as_file(template_root) as path:
        config = {
            "template_root": path,
            "output_root": output_dir,
            "project_root": cwd,
            "encoding": "utf-8",
            "config_path": yaml_path,
        }
        return Container(config=config)


def _get_default_package_path(root_path: Path) -> Path:
    """Get default package path for reverse engineering relative to root path."""
    # MODIFIED: Use passed root_path instead of Path.cwd()
    cwd = root_path
    src_dir = cwd / "src"
    if src_dir.exists():
        pkgs = [
            p for p in src_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
        ]
        path = pkgs[0] if pkgs else src_dir
    else:
        path = cwd
    return path


def _serialize_value(value: Any, output_format: str = "json") -> str:
    """Serialize value to string for output."""
    if isinstance(value, BaseModel):
        if output_format == "yaml":
            import yaml
            return yaml.dump(value.model_dump(), allow_unicode=True, default_flow_style=False)
        return value.model_dump_json(indent=2)

    if isinstance(value, (list, dict)):
        if output_format == "yaml":
            import yaml

            def to_dict(obj: Any) -> Any:
                if isinstance(obj, BaseModel):
                    return obj.model_dump()
                if isinstance(obj, list):
                    return [to_dict(item) for item in obj]
                if isinstance(obj, dict):
                    return {k: to_dict(v) for k, v in obj.items()}
                return obj

            return yaml.dump(to_dict(value), allow_unicode=True, default_flow_style=False)
        return json.dumps(
            value if not any(isinstance(v, BaseModel) for v in (value if isinstance(value, list) else [value]))
            else [v.model_dump() if isinstance(v, BaseModel) else v for v in value] if isinstance(value, list)
            else value,
            indent=2,
            ensure_ascii=False,
            default=lambda o: o.model_dump() if isinstance(o, BaseModel) else str(o)
        )

    return str(value)


def _parse_value(value_str: str) -> Any:
    """Parse value string - tries JSON first, falls back to string."""
    if not value_str:
        return value_str
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        return value_str


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool()
def build(
        work_dir: str,
        config_file: str = "codegen.yaml",
        output: str = "src",
        node: str | None = None,
) -> BuildResult:
    """
    Build: Compile codegen.yaml into Python code.

    This is the primary code generation command. It reads your blueprint
    file and generates Python code based on DDD patterns.

    Args:
        work_dir: Absolute path to the project root directory
        config_file: Path to the codegen.yaml blueprint file (relative to work_dir)
        output: Output directory - "src" (default) or custom path (relative or absolute)
        node: Generate only a specific component by name (overwrite mode enabled).
    """
    root_path = Path(work_dir).resolve()
    config_path = Path(config_file)

    container = _get_container(
        config_file=config_path,
        root_path=root_path,
        output=output,
    )
    use_case = container.generate_project_use_case()

    # When node is specified, overwrite is automatically enabled
    overwrite = node is not None

    root_path_str = "" if output == "src" else output.replace("/", ".").replace("\\", ".")

    cmd = GenerateProjectCommand(overwrite=overwrite, node=node, root_path=root_path_str)
    r = use_case.execute(cmd)

    return r.result


@mcp.tool()
def reverse(
        work_dir: str,
        config_file: str = "codegen.yaml",
        package_path: str | None = None,
) -> str:
    """
    Reverse: Reverse-engineer Python code into codegen.yaml.

    This command analyzes an existing Python package and generates
    a codegen.yaml blueprint that describes its structure.

    Args:
        work_dir: Absolute path to the project root directory
        config_file: Path to output codegen.yaml blueprint file
        package_path: Path to existing Python package to reverse engineer
    """
    try:
        # MODIFIED: Resolve work_dir
        root_path = Path(work_dir).resolve()
        config_path = Path(config_file)

        container = _get_container(config_file=config_path, root_path=root_path)

        pkg_path = Path(package_path) if package_path else _get_default_package_path(root_path)
        # Ensure pkg_path is absolute or relative to root_path correctly
        if not pkg_path.is_absolute():
            pkg_path = root_path / pkg_path

        use_case = container.update_blueprint_use_case()
        cmd = GenerateBlueprintCommand(path=pkg_path)
        use_case.execute(cmd)

        return f"Reverse engineering completed. Blueprint saved to {config_file}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def tree(
        work_dir: str,
        config_file: str = "codegen.yaml",
        path: str | None = None,
        depth: int = -1,
        detail: bool = False,
) -> str:
    """
    Tree: Display blueprint structure as a visual tree.

    Provides a hierarchical overview of your project's DDD structure.

    Args:
        work_dir: Absolute path to the project root directory
        config_file: Path to the codegen.yaml blueprint file
        path: Optional path to start from (e.g., 'contexts.DomainDefinition')
        depth: Maximum depth to display (-1 for unlimited)
        detail: Show descriptions alongside names
    """
    try:
        from io import StringIO
        from rich.console import Console
        from rich.tree import Tree as RichTree

        # Import tree helpers from CLI module
        from codegen.entrypoints.cli.commands.tree import (
            add_item_to_tree,
            add_model_children,
        )

        # MODIFIED: Resolve work_dir
        root_path = Path(work_dir).resolve()
        config_path = Path(config_file)

        container = _get_container(config_file=config_path, root_path=root_path)

        # Load the blueprint
        load_use_case = container.load_blueprint_use_case()
        result = load_use_case.execute(LoadBlueprintCommand())

        if not result or not result.blueprint:
            return "Error: Blueprint not found"

        blueprint = result.blueprint

        # If path specified, navigate to that location
        target = blueprint
        root_label = f"📦 Project: {blueprint.name}"

        if path:
            get_use_case = container.get_value_use_case()
            target = get_use_case.execute(GetValueCommand(path=path))
            root_label = f"📍 {path}"

        # Build the tree
        root = RichTree(root_label)

        if isinstance(target, list):
            for item in target:
                add_item_to_tree(item, root, 0, depth, detail)
        elif isinstance(target, BaseModel):
            add_model_children(target, root, 0, depth, detail)
        else:
            root.add(str(target))

        # Render to string
        output = StringIO()
        console = Console(file=output, force_terminal=False, no_color=True, width=120)
        console.print(root)

        return output.getvalue()
    except KeyError as e:
        return f"Error: Path not found - {e}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get(
        work_dir: str,
        path: str,
        config_file: str = "codegen.yaml",
        output_format: str = "json",
) -> str:
    """
    Get: Query a value from blueprint by path.

    Args:
        work_dir: Absolute path to the project root directory
        path: Path to query (e.g., 'project.name', 'contexts.sales.aggregates')
        config_file: Path to the codegen.yaml blueprint file
        output_format: Output format: json or yaml
    """
    try:
        # MODIFIED: Resolve work_dir
        root_path = Path(work_dir).resolve()
        config_path = Path(config_file)

        container = _get_container(config_file=config_path, root_path=root_path)

        use_case = container.get_value_use_case()
        result = use_case.execute(GetValueCommand(path=path))

        return _serialize_value(result, output_format)
    except KeyError as e:
        return f"Error: Path not found - {e}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def set(
        work_dir: str,
        path: str,
        value: str,
        config_file: str = "codegen.yaml",
        append: bool = False,
) -> str:
    """
    Set: Set or update a value in blueprint by path (Upsert).

    Args:
        work_dir: Absolute path to the project root directory
        path: Path to set (e.g., 'project.version', 'contexts.sales.aggregates')
        value: JSON value to set
        config_file: Path to the codegen.yaml blueprint file
        append: Append to list instead of replace
    """
    try:
        # MODIFIED: Resolve work_dir
        root_path = Path(work_dir).resolve()
        config_path = Path(config_file)
        parsed_value = _parse_value(value)

        container = _get_container(config_file=config_path, root_path=root_path)
        use_case = container.set_value_use_case()

        use_case.execute(SetValueCommand(
            path=path,
            value=parsed_value,
            append=append,
        ))

        return f"Successfully set value at '{path}'"
    except KeyError as e:
        return f"Error: Path not found - {e}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def rm(
        work_dir: str,
        path: str,
        config_file: str = "codegen.yaml",
) -> str:
    """
    Remove: Delete a value from blueprint by path.

    Args:
        work_dir: Absolute path to the project root directory
        path: Path to remove (e.g., 'contexts.sales', 'contexts[0]')
        config_file: Path to the codegen.yaml blueprint file
    """
    try:
        # MODIFIED: Resolve work_dir
        root_path = Path(work_dir).resolve()
        config_path = Path(config_file)

        container = _get_container(config_file=config_path, root_path=root_path)

        use_case = container.remove_value_use_case()
        use_case.execute(RemoveValueCommand(path=path))

        return f"Successfully removed '{path}'"
    except KeyError as e:
        return f"Error: Path not found - {e}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run()