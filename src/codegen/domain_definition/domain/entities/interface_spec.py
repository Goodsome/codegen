from typing import TYPE_CHECKING, Self

from codegen.shared.domain.core import Entity
from codegen.domain_definition.domain.value_objects.cli_command_spec import (
    CliCommandSpec,
)
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import (
    HttpEndpointSpec,
)
from codegen.shared.domain.value_objects.kebab_string import KebabString
from pydantic import Field

if TYPE_CHECKING:
    from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
    from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


class InterfaceSpec(Entity):
    """接口层总规范"""

    cli_commands: list[CliCommandSpec] = Field(default_factory=list)
    mcp_tools: list[McpToolSpec] = Field(default_factory=list)
    http_endpoints: list[HttpEndpointSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        context_name: str,
        use_cases: list["UseCaseSpec"],
        project_name: str = "",
    ) -> "PackageSpec":
        """将 InterfaceSpec 转换为 PackageSpec

        Args:
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for interfaces package
        """
        from codegen.python_gen.domain.value_objects.package_spec import PackageSpec

        sub_packages: list["PackageSpec"] = []

        if self.cli_commands:
            cli_pkg = CliCommandSpec.commands_to_package_spec(
                self.cli_commands, context_name, use_cases, project_name
            )
            sub_packages.append(cli_pkg)

        if self.mcp_tools:
            mcp_pkg = McpToolSpec.tools_to_package_spec(
                self.mcp_tools, context_name, use_cases, project_name
            )
            sub_packages.append(mcp_pkg)

        if self.http_endpoints:
            http_pkg = HttpEndpointSpec.endpoints_to_package_spec(
                self.http_endpoints, context_name, use_cases, project_name
            )
            sub_packages.append(http_pkg)

        return PackageSpec.create(
            name="interfaces",
            sub_packages=sub_packages,
        )

    @classmethod
    def from_package_spec(
        cls,
        interfaces_pkg: "PackageSpec",
        use_cases: list["UseCaseSpec"],
    ) -> "InterfaceSpec":
        """从 PackageSpec 逆向解析为 InterfaceSpec

        Args:
            interfaces_pkg: interfaces 包的 PackageSpec
            use_cases: UseCase 列表，用于索引

        Returns:
            InterfaceSpec
        """
        cli_commands: list[CliCommandSpec] = []
        mcp_tools: list[McpToolSpec] = []
        http_endpoints: list[HttpEndpointSpec] = []

        for sub_pkg in interfaces_pkg.sub_packages:
            if sub_pkg.name == "cli":
                cli_commands = CliCommandSpec.commands_from_package_spec(
                    sub_pkg, use_cases
                )
            elif sub_pkg.name == "mcp":
                mcp_tools = McpToolSpec.tools_from_package_spec(sub_pkg, use_cases)
            elif sub_pkg.name == "http":
                http_endpoints = HttpEndpointSpec.endpoints_from_package_spec(
                    sub_pkg, use_cases
                )

        return cls(
            cli_commands=cli_commands,
            mcp_tools=mcp_tools,
            http_endpoints=http_endpoints,
        )

    def add_cli_command(self, cli_command: CliCommandSpec) -> Self:
        """Add a CliCommandSpec. Raises ValueError if cli_command with same name exists."""
        for cmd in self.cli_commands:
            if cmd.name == cli_command.name:
                raise ValueError(
                    f"CliCommand '{cli_command.name}' already exists in interface"
                )
        self.cli_commands.append(cli_command)
        return self

    def update_cli_command(self, cli_command: CliCommandSpec) -> Self:
        """Update an existing CliCommandSpec by name. Raises ValueError if not found."""
        for i, cmd in enumerate(self.cli_commands):
            if cmd.name == cli_command.name:
                self.cli_commands[i] = cli_command
                return self
        raise ValueError(f"CliCommand '{cli_command.name}' not found in interface")

    def remove_cli_command(self, name: KebabString) -> Self:
        """Remove a CliCommandSpec by name. Returns self for chaining."""
        self.cli_commands = [cmd for cmd in self.cli_commands if cmd.name != name]
        return self

    def get_cli_command(self, name: KebabString) -> CliCommandSpec:
        """Get a CliCommandSpec by name. Raises ValueError if not found."""
        for cmd in self.cli_commands:
            if cmd.name == name:
                return cmd
        raise ValueError(f"CliCommand '{name}' not found in interface")

    def add_mcp_tool(self, mcp_tool: McpToolSpec) -> Self:
        """Add an McpToolSpec. Raises ValueError if mcp_tool with same name exists."""
        for tool in self.mcp_tools:
            if tool.name == mcp_tool.name:
                raise ValueError(
                    f"McpTool '{mcp_tool.name}' already exists in interface"
                )
        self.mcp_tools.append(mcp_tool)
        return self

    def update_mcp_tool(self, mcp_tool: McpToolSpec) -> Self:
        """Update an existing McpToolSpec by name. Raises ValueError if not found."""
        for i, tool in enumerate(self.mcp_tools):
            if tool.name == mcp_tool.name:
                self.mcp_tools[i] = mcp_tool
                return self
        raise ValueError(f"McpTool '{mcp_tool.name}' not found in interface")

    def remove_mcp_tool(self, name: str) -> Self:
        """Remove an McpToolSpec by name. Returns self for chaining."""
        self.mcp_tools = [tool for tool in self.mcp_tools if tool.name != name]
        return self

    def get_mcp_tool(self, name: str) -> McpToolSpec:
        """Get an McpToolSpec by name. Raises ValueError if not found."""
        for tool in self.mcp_tools:
            if tool.name == name:
                return tool
        raise ValueError(f"McpTool '{name}' not found in interface")

    def add_http_endpoint(self, http_endpoint: HttpEndpointSpec) -> Self:
        """Add an HttpEndpointSpec. Raises ValueError if http_endpoint with same name exists."""
        for endpoint in self.http_endpoints:
            if endpoint.name == http_endpoint.name:
                raise ValueError(
                    f"HttpEndpoint '{http_endpoint.name}' already exists in interface"
                )
        self.http_endpoints.append(http_endpoint)
        return self

    def update_http_endpoint(self, http_endpoint: HttpEndpointSpec) -> Self:
        """Update an existing HttpEndpointSpec by name. Raises ValueError if not found."""
        for i, endpoint in enumerate(self.http_endpoints):
            if endpoint.name == http_endpoint.name:
                self.http_endpoints[i] = http_endpoint
                return self
        raise ValueError(f"HttpEndpoint '{http_endpoint.name}' not found in interface")

    def remove_http_endpoint(self, name: str) -> Self:
        """Remove an HttpEndpointSpec by name. Returns self for chaining."""
        self.http_endpoints = [
            endpoint for endpoint in self.http_endpoints if endpoint.name != name
        ]
        return self

    def get_http_endpoint(self, name: str) -> HttpEndpointSpec:
        """Get an HttpEndpointSpec by name. Raises ValueError if not found."""
        for endpoint in self.http_endpoints:
            if endpoint.name == name:
                return endpoint
        raise ValueError(f"HttpEndpoint '{name}' not found in interface")
