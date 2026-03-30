from typing import TYPE_CHECKING

from codegen.shared.models import Entity
from codegen.domain_definition.domain.value_objects.cli_command_spec import CliCommandSpec
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import HttpEndpointSpec
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
                cli_commands = CliCommandSpec.commands_from_package_spec(sub_pkg, use_cases)
            elif sub_pkg.name == "mcp":
                mcp_tools = McpToolSpec.tools_from_package_spec(sub_pkg, use_cases)
            elif sub_pkg.name == "http":
                http_endpoints = HttpEndpointSpec.endpoints_from_package_spec(sub_pkg, use_cases)

        return cls(
            cli_commands=cli_commands,
            mcp_tools=mcp_tools,
            http_endpoints=http_endpoints,
        )