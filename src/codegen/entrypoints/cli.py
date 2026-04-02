import typer

from codegen.bootstrap import bootstrap
from codegen.orchestration.interfaces.cli.build import build
from codegen.orchestration.interfaces.cli.reverse import reverse
from codegen.python_gen.interfaces.cli.schema import schema
from codegen.domain_definition.interfaces.cli.tree import tree as tree_cmd
from codegen.domain_definition.interfaces.cli.init import init

# Domain layer commands
from codegen.domain_definition.interfaces.cli.add_aggregate import add_aggregate
from codegen.domain_definition.interfaces.cli.update_aggregate import update_aggregate
from codegen.domain_definition.interfaces.cli.get_aggregate import get_aggregate
from codegen.domain_definition.interfaces.cli.remove_aggregate import remove_aggregate
from codegen.domain_definition.interfaces.cli.add_entity import add_entity
from codegen.domain_definition.interfaces.cli.update_entity import update_entity
from codegen.domain_definition.interfaces.cli.get_entity import get_entity
from codegen.domain_definition.interfaces.cli.remove_entity import remove_entity
from codegen.domain_definition.interfaces.cli.add_value_object import add_value_object
from codegen.domain_definition.interfaces.cli.update_value_object import update_value_object
from codegen.domain_definition.interfaces.cli.get_value_object import get_value_object
from codegen.domain_definition.interfaces.cli.remove_value_object import remove_value_object
from codegen.domain_definition.interfaces.cli.add_enum import add_enum
from codegen.domain_definition.interfaces.cli.update_enum import update_enum
from codegen.domain_definition.interfaces.cli.get_enum import get_enum
from codegen.domain_definition.interfaces.cli.remove_enum import remove_enum
from codegen.domain_definition.interfaces.cli.add_domain_service import add_domain_service
from codegen.domain_definition.interfaces.cli.update_domain_service import update_domain_service
from codegen.domain_definition.interfaces.cli.get_domain_service import get_domain_service
from codegen.domain_definition.interfaces.cli.remove_domain_service import remove_domain_service
from codegen.domain_definition.interfaces.cli.add_domain_port import add_domain_port
from codegen.domain_definition.interfaces.cli.update_domain_port import update_domain_port
from codegen.domain_definition.interfaces.cli.get_domain_port import get_domain_port
from codegen.domain_definition.interfaces.cli.remove_domain_port import remove_domain_port

# App layer commands
from codegen.domain_definition.interfaces.cli.add_use_case import add_use_case
from codegen.domain_definition.interfaces.cli.update_use_case import update_use_case
from codegen.domain_definition.interfaces.cli.get_use_case import get_use_case
from codegen.domain_definition.interfaces.cli.remove_use_case import remove_use_case
from codegen.domain_definition.interfaces.cli.add_app_port import add_app_port
from codegen.domain_definition.interfaces.cli.update_app_port import update_app_port
from codegen.domain_definition.interfaces.cli.get_app_port import get_app_port
from codegen.domain_definition.interfaces.cli.remove_app_port import remove_app_port
from codegen.domain_definition.interfaces.cli.add_app_service import add_app_service
from codegen.domain_definition.interfaces.cli.update_app_service import update_app_service
from codegen.domain_definition.interfaces.cli.get_app_service import get_app_service
from codegen.domain_definition.interfaces.cli.remove_app_service import remove_app_service

# Infrastructure layer commands
from codegen.domain_definition.interfaces.cli.add_implementation import add_implementation
from codegen.domain_definition.interfaces.cli.update_implementation import update_implementation
from codegen.domain_definition.interfaces.cli.get_implementation import get_implementation
from codegen.domain_definition.interfaces.cli.remove_implementation import remove_implementation

# Interface layer commands
from codegen.domain_definition.interfaces.cli.add_cli_command import add_cli_command
from codegen.domain_definition.interfaces.cli.update_cli_command import update_cli_command
from codegen.domain_definition.interfaces.cli.get_cli_command import get_cli_command
from codegen.domain_definition.interfaces.cli.remove_cli_command import remove_cli_command
from codegen.domain_definition.interfaces.cli.add_mcp_tool import add_mcp_tool
from codegen.domain_definition.interfaces.cli.update_mcp_tool import update_mcp_tool
from codegen.domain_definition.interfaces.cli.get_mcp_tool import get_mcp_tool
from codegen.domain_definition.interfaces.cli.remove_mcp_tool import remove_mcp_tool
from codegen.domain_definition.interfaces.cli.add_http_endpoint import add_http_endpoint
from codegen.domain_definition.interfaces.cli.update_http_endpoint import update_http_endpoint
from codegen.domain_definition.interfaces.cli.get_http_endpoint import get_http_endpoint
from codegen.domain_definition.interfaces.cli.remove_http_endpoint import remove_http_endpoint

# Field commands (attribute and method CRUD)
from codegen.domain_definition.interfaces.cli.add_attribute import add_attribute
from codegen.domain_definition.interfaces.cli.update_attribute import update_attribute
from codegen.domain_definition.interfaces.cli.remove_attribute import remove_attribute
from codegen.domain_definition.interfaces.cli.add_method import add_method
from codegen.domain_definition.interfaces.cli.update_method import update_method
from codegen.domain_definition.interfaces.cli.remove_method import remove_method

app = typer.Typer(
    name="codegen",
    help="""Codegen CLI - DDD Project Scaffolding Tool.

**Core Commands (Lifecycle)**:
  init       Initialize a new codegen.yaml blueprint
  build      Compile codegen.yaml into Python code
  reverse    Reverse-engineer Python code into codegen.yaml
  schema     Output JSON schema for the blueprint

**Overview Command**:
  tree       Display blueprint structure as a visual tree

**Domain Commands**:
  domain     Manage domain model elements (aggregates, entities, value objects, enums, services, ports)

**App Commands**:
  app        Manage application layer elements (use cases, ports, services)

**Infrastructure Commands**:
  infrastructure  Manage infrastructure implementations

**Interface Commands**:
  interface   Manage interface elements (CLI commands, MCP tools, HTTP endpoints)

**Field Commands**:
  field       Manage fields (attributes, dependencies, inputs, outputs, methods)

    """,
    add_completion=False,
    rich_markup_mode="markdown",
)

domain_app = typer.Typer(help="Domain model manipulation commands")
app.add_typer(domain_app, name="domain")

app_app = typer.Typer(help="Application layer manipulation commands")
app.add_typer(app_app, name="app")

infrastructure_app = typer.Typer(help="Infrastructure manipulation commands")
app.add_typer(infrastructure_app, name="infrastructure")

interface_app = typer.Typer(help="Interface layer manipulation commands")
app.add_typer(interface_app, name="interface")

field_app = typer.Typer(help="Field manipulation commands (attributes, methods)")
app.add_typer(field_app, name="field")

# ============================================================================
# Root Commands
# ============================================================================

app.command()(build)
app.command()(reverse)
app.command()(schema)
app.command()(init)
app.command(name="tree")(tree_cmd)

# ============================================================================
# Domain Commands
# ============================================================================

domain_app.command(name="add-aggregate")(add_aggregate)
domain_app.command(name="update-aggregate")(update_aggregate)
domain_app.command(name="get-aggregate")(get_aggregate)
domain_app.command(name="remove-aggregate")(remove_aggregate)
domain_app.command(name="add-entity")(add_entity)
domain_app.command(name="update-entity")(update_entity)
domain_app.command(name="get-entity")(get_entity)
domain_app.command(name="remove-entity")(remove_entity)
domain_app.command(name="add-value-object")(add_value_object)
domain_app.command(name="update-value-object")(update_value_object)
domain_app.command(name="get-value-object")(get_value_object)
domain_app.command(name="remove-value-object")(remove_value_object)
domain_app.command(name="add-enum")(add_enum)
domain_app.command(name="update-enum")(update_enum)
domain_app.command(name="get-enum")(get_enum)
domain_app.command(name="remove-enum")(remove_enum)
domain_app.command(name="add-domain-service")(add_domain_service)
domain_app.command(name="update-domain-service")(update_domain_service)
domain_app.command(name="get-domain-service")(get_domain_service)
domain_app.command(name="remove-domain-service")(remove_domain_service)
domain_app.command(name="add-domain-port")(add_domain_port)
domain_app.command(name="update-domain-port")(update_domain_port)
domain_app.command(name="get-domain-port")(get_domain_port)
domain_app.command(name="remove-domain-port")(remove_domain_port)

# ============================================================================
# App Commands
# ============================================================================

app_app.command(name="add-use-case")(add_use_case)
app_app.command(name="update-use-case")(update_use_case)
app_app.command(name="get-use-case")(get_use_case)
app_app.command(name="remove-use-case")(remove_use_case)
app_app.command(name="add-app-port")(add_app_port)
app_app.command(name="update-app-port")(update_app_port)
app_app.command(name="get-app-port")(get_app_port)
app_app.command(name="remove-app-port")(remove_app_port)
app_app.command(name="add-app-service")(add_app_service)
app_app.command(name="update-app-service")(update_app_service)
app_app.command(name="get-app-service")(get_app_service)
app_app.command(name="remove-app-service")(remove_app_service)

# ============================================================================
# Infrastructure Commands
# ============================================================================

infrastructure_app.command(name="add-implementation")(add_implementation)
infrastructure_app.command(name="update-implementation")(update_implementation)
infrastructure_app.command(name="get-implementation")(get_implementation)
infrastructure_app.command(name="remove-implementation")(remove_implementation)

# ============================================================================
# Interface Commands
# ============================================================================

interface_app.command(name="add-cli-command")(add_cli_command)
interface_app.command(name="update-cli-command")(update_cli_command)
interface_app.command(name="get-cli-command")(get_cli_command)
interface_app.command(name="remove-cli-command")(remove_cli_command)
interface_app.command(name="add-mcp-tool")(add_mcp_tool)
interface_app.command(name="update-mcp-tool")(update_mcp_tool)
interface_app.command(name="get-mcp-tool")(get_mcp_tool)
interface_app.command(name="remove-mcp-tool")(remove_mcp_tool)
interface_app.command(name="add-http-endpoint")(add_http_endpoint)
interface_app.command(name="update-http-endpoint")(update_http_endpoint)
interface_app.command(name="get-http-endpoint")(get_http_endpoint)
interface_app.command(name="remove-http-endpoint")(remove_http_endpoint)

# ============================================================================
# Field Commands
# ============================================================================

field_app.command(name="add")(add_attribute)
field_app.command(name="update")(update_attribute)
field_app.command(name="remove")(remove_attribute)
field_app.command(name="add-method")(add_method)
field_app.command(name="update-method")(update_method)
field_app.command(name="remove-method")(remove_method)


def main():
    """Bootstrap the DI container and run the CLI app."""
    container = bootstrap()
    container.wire(packages=[
        "codegen.orchestration.interfaces.cli",
        "codegen.domain_definition.interfaces.cli",
        "codegen.python_gen.interfaces.cli",
    ])
    app()


if __name__ == "__main__":
    main()
