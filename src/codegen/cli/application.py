import typer
from codegen.cli.utils import version_callback

from codegen.cli.commands.generate import app as generate_app
from codegen.cli.commands.add import app as add_app
from codegen.cli.commands.update import app as update_app
from codegen.cli.commands.delete import app as delete_app

app = typer.Typer(
    name="codegen",
    help="""A DDD (Domain-Driven Design) Project Scaffolding Tool.

    Codegen reads a codegen.yaml blueprint file that defines your project structure
    and generates Python code based on DDD patterns. It can also reverse-engineer
    existing Python packages back into a codegen.yaml blueprint.

    Common commands:
    - codegen generate              Generate code from codegen.yaml
    - codegen generate-blueprint    Reverse engineer Python package to blueprint
    - codegen generate-blueprint-schema  Generate JSON schema for blueprint
        

    For more information, see: https://github.com/Goodsome/codegen
    """,
    add_completion=False,
    rich_markup_mode="markdown",
)

# Merge commands from generate_app into the main app directly
# Note: Typer doesn't easily support merging commands from another typer instance into root
# without using add_typer. But generate commands are on root in original CLI.
# To keep backward compatibility (codegen generate ...), we can register them manually or use a workaround.
# For simplicity and modularity, we might want to keep them as subcommands if possible, 
# OR just import the functions and register them.
# Let's import the functions and register them to maintain `codegen generate` syntax.

from codegen.cli.commands.generate import generate, generate_blueprint, generate_blueprint_schema

app.command()(generate)
app.command(name="generate-blueprint")(generate_blueprint)
app.command(name="generate-blueprint-schema")(generate_blueprint_schema)

# Register Sub-apps
app.add_typer(add_app, name="add")
app.add_typer(update_app, name="update")
app.add_typer(delete_app, name="delete")


if __name__ == "__main__":
    app()
