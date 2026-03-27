import typer
from codegen.python_gen.interfaces.cli.schema import schema

app = typer.Typer(help="PythonGen CLI")
app.command("schema")(schema)
