from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.cli_interface_spec import CliInterfaceSpec
from codegen.domain_definition.domain.value_objects.mcp_interface_spec import McpInterfaceSpec
from codegen.domain_definition.domain.value_objects.http_interface_spec import HttpInterfaceSpec


class InterfaceSpec(ValueObject):
    """接口层总规范"""

    cli: CliInterfaceSpec | None = None
    mcp: McpInterfaceSpec | None = None
    http: HttpInterfaceSpec | None = None