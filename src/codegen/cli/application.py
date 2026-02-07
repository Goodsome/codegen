import typer
from codegen.cli.utils import version_callback

# New path-based commands
from codegen.cli.commands.build import build
from codegen.cli.commands.reverse import reverse
from codegen.cli.commands.schema import schema
from codegen.cli.commands.get import get as get_cmd
from codegen.cli.commands.set import set as set_cmd
from codegen.cli.commands.rm import rm

# Legacy commands (for backward compatibility)
from codegen.cli.commands.generate import generate, generate_blueprint, generate_blueprint_schema
from codegen.cli.commands.add import app as add_app
from codegen.cli.commands.update import app as update_app
from codegen.cli.commands.delete import app as delete_app

app = typer.Typer(
    name="codegen",
    help="""Codegen CLI - DDD Project Scaffolding Tool.

**Core Commands (Lifecycle)**:
  build      Compile codegen.yaml into Python code
  reverse    Reverse-engineer Python code into codegen.yaml
  schema     Output JSON schema for the blueprint

**Edit Commands (Blueprint Manipulation)**:
  get        Get a value by path (e.g., 'contexts.sales')
  set        Set a value by path (Upsert). Supports --append for lists
  rm         Remove a value by path

**Options**:
  -c, --config PATH   Path to codegen.yaml [default: ./codegen.yaml]
  --help              Show this message

**Examples**:
  $ codegen build --overwrite
  $ codegen set "project.version" '"1.2.0"'
  $ codegen get "contexts.DomainDefinition.domain.aggregates"
  $ codegen rm "contexts.Test"

For more information, see: https://github.com/Goodsome/codegen
    """,
    add_completion=False,
    rich_markup_mode="markdown",
)

# ============================================================================
# New Path-Based Commands (Primary)
# ============================================================================

app.command()(build)
app.command()(reverse)
app.command()(schema)
app.command(name="get")(get_cmd)
app.command(name="set")(set_cmd)
app.command()(rm)

# ============================================================================
# Legacy Commands (Backward Compatibility - Deprecated)
# ============================================================================

# Old generate commands - kept for backward compatibility
app.command(name="generate", deprecated=True, help="[DEPRECATED] Use 'build' instead. Generate code from codegen.yaml")(generate)
app.command(name="generate-blueprint", deprecated=True, help="[DEPRECATED] Use 'reverse' instead. Reverse engineer Python package")(generate_blueprint)
app.command(name="generate-blueprint-schema", deprecated=True, help="[DEPRECATED] Use 'schema' instead. Generate JSON schema")(generate_blueprint_schema)

# Old sub-apps - kept for backward compatibility
app.add_typer(add_app, name="add", deprecated=True, help="[DEPRECATED] Use 'set --append' instead. Add components")
app.add_typer(update_app, name="update", deprecated=True, help="[DEPRECATED] Use 'set' instead. Update components")
app.add_typer(delete_app, name="delete", deprecated=True, help="[DEPRECATED] Use 'rm' instead. Delete components")


if __name__ == "__main__":
    app()
