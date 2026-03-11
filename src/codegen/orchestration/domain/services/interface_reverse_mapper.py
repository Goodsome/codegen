from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.interface_spec import InterfaceSpec
from codegen.domain_definition.domain.value_objects.cli_interface_spec import CliInterfaceSpec
from codegen.domain_definition.domain.value_objects.cli_command_spec import CliCommandSpec
from codegen.domain_definition.domain.value_objects.mcp_interface_spec import McpInterfaceSpec
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec
from codegen.domain_definition.domain.value_objects.http_interface_spec import HttpInterfaceSpec
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import HttpEndpointSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


@dataclass
class InterfaceReverseMapper:
    """Interfaces Reverse 解析器，从目录和文件名推断接口定义"""

    def to_interface_spec(
        self,
        interfaces_pkg: PackageSpec,
        use_cases: list[UseCaseSpec],
    ) -> InterfaceSpec:
        """从 PackageSpec 解析 InterfaceSpec"""
        use_case_index = {uc.name: uc for uc in use_cases}

        cli_spec = None
        mcp_spec = None
        http_spec = None

        for sub_pkg in interfaces_pkg.sub_packages:
            if sub_pkg.name == "cli":
                cli_spec = self._parse_cli_interface(sub_pkg, use_case_index)
            elif sub_pkg.name == "mcp":
                mcp_spec = self._parse_mcp_interface(sub_pkg, use_case_index)
            elif sub_pkg.name == "http":
                http_spec = self._parse_http_interface(sub_pkg, use_case_index)

        return InterfaceSpec(cli=cli_spec, mcp=mcp_spec, http=http_spec)

    def _parse_cli_interface(
        self,
        cli_pkg: PackageSpec,
        use_case_index: dict[str, UseCaseSpec],
    ) -> CliInterfaceSpec:
        """解析 CLI 接口"""
        commands: list[CliCommandSpec] = []

        for module in cli_pkg.modules:
            if module.name == "__init__":
                continue

            # 从模块名推断命令名
            cmd_name = str(module.name).replace("_", "-")

            # 从函数中推断 UseCase
            for func in module.functions:
                use_case_name = self._infer_use_case_from_suite(func.suite, use_case_index)
                if use_case_name:
                    commands.append(CliCommandSpec(
                        name=cmd_name,
                        use_case=use_case_name,
                        description=func.suite.split("\n")[0] if func.suite else "",
                    ))
                    break  # 每个模块只取第一个函数

        return CliInterfaceSpec(commands=commands)

    def _parse_mcp_interface(
        self,
        mcp_pkg: PackageSpec,
        use_case_index: dict[str, UseCaseSpec],
    ) -> McpInterfaceSpec:
        """解析 MCP 接口"""
        tools: list[McpToolSpec] = []

        for module in mcp_pkg.modules:
            if module.name == "__init__":
                continue

            # 从模块名推断 tool 名
            tool_name = str(module.name)

            # 从函数中推断 UseCase
            for func in module.functions:
                use_case_name = self._infer_use_case_from_suite(func.suite, use_case_index)
                if use_case_name:
                    tools.append(McpToolSpec(
                        name=tool_name,
                        use_case=use_case_name,
                        description=func.suite.split("\n")[0] if func.suite else "",
                    ))
                    break

        return McpInterfaceSpec(tools=tools)

    def _parse_http_interface(
        self,
        http_pkg: PackageSpec,
        use_case_index: dict[str, UseCaseSpec],
    ) -> HttpInterfaceSpec:
        """解析 HTTP 接口"""
        endpoints: list[HttpEndpointSpec] = []

        for module in http_pkg.modules:
            if module.name == "__init__":
                continue

            # 从函数装饰器推断 path 和 method
            for func in module.functions:
                path, method = self._parse_route_decorator(func.decorators)
                if path and method:
                    use_case_name = self._infer_use_case_from_suite(func.suite, use_case_index)
                    if use_case_name:
                        endpoints.append(HttpEndpointSpec(
                            path=path,
                            method=method,
                            use_case=use_case_name,
                            description=func.suite.split("\n")[0] if func.suite else "",
                        ))

        return HttpInterfaceSpec(endpoints=endpoints)

    def _infer_use_case_from_suite(
        self,
        suite: str,
        use_case_index: dict[str, UseCaseSpec],
    ) -> str | None:
        """从函数体推断 UseCase 名称"""
        # 查找 container.xxx_use_case() 模式
        import re
        pattern = r'container\.(\w+)_use_case\(\)'
        match = re.search(pattern, suite)
        if match:
            method_name = match.group(1)
            # 将 snake_case 转换为 PascalCase
            use_case_name = ''.join(word.capitalize() for word in method_name.split('_'))
            if use_case_name in use_case_index:
                return use_case_name
        return None

    def _parse_route_decorator(self, decorators: list[str]) -> tuple[str | None, str | None]:
        """从装饰器解析路由信息"""
        import re
        for decorator in decorators:
            # 匹配 router.get("/path"), router.post("/path") 等
            match = re.match(r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)', decorator)
            if match:
                method = match.group(1).upper()
                path = match.group(2)
                return path, method
        return None, None