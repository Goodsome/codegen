from dataclasses import dataclass, field
from typing import Any

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.interface_spec import InterfaceSpec
from codegen.domain_definition.domain.value_objects.cli_command_spec import CliCommandSpec
from codegen.domain_definition.domain.value_objects.cli_interface_spec import CliInterfaceSpec
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec
from codegen.domain_definition.domain.value_objects.mcp_interface_spec import McpInterfaceSpec
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import HttpEndpointSpec
from codegen.domain_definition.domain.value_objects.http_interface_spec import HttpInterfaceSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str


@dataclass
class InterfaceMapper:
    """Interfaces 层代码生成器"""

    def to_package_spec(
        self,
        interfaces: InterfaceSpec,
        context_name: str,
        use_cases: list[UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """将 InterfaceSpec 转换为 PackageSpec"""
        use_case_index = {uc.name: uc for uc in use_cases}
        sub_packages: list[PackageSpec] = []

        if interfaces.cli:
            cli_pkg = self._map_cli_interface(interfaces.cli, context_name, use_case_index, project_name)
            sub_packages.append(cli_pkg)

        if interfaces.mcp:
            mcp_pkg = self._map_mcp_interface(interfaces.mcp, context_name, use_case_index, project_name)
            sub_packages.append(mcp_pkg)

        if interfaces.http:
            http_pkg = self._map_http_interface(interfaces.http, context_name, use_case_index, project_name)
            sub_packages.append(http_pkg)

        return PackageSpec.create(
            name="interfaces",
            sub_packages=sub_packages,
        )

    def _map_cli_interface(
        self,
        cli_spec: Any,
        context_name: str,
        use_case_index: dict[str, UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """生成 CLI 接口包"""
        modules: list[ModuleSpec] = []
        function_names: list[str] = []

        for cmd in cli_spec.commands:
            module = self._map_cli_command(cmd, context_name, use_case_index, project_name)
            modules.append(module)
            function_names.append(cmd.name.replace("-", "_"))

        # 生成 __init__.py
        init_module = self._create_cli_init_module(context_name, function_names, project_name)
        modules.append(init_module)

        return PackageSpec.create(
            name="cli",
            modules=modules,
        )

    def _map_cli_command(
        self,
        cmd: CliCommandSpec,
        context_name: str,
        use_case_index: dict[str, UseCaseSpec],
        project_name: str = "",
    ) -> ModuleSpec:
        """生成单个 CLI 命令模块"""
        use_case = use_case_index.get(cmd.use_case)
        if not use_case:
            raise ValueError(f"UseCase '{cmd.use_case}' not found for CLI command '{cmd.name}'")

        # 确定参数类型
        if use_case.kind == UseCaseKind.COMMAND:
            param_type = f"{use_case.name}Command"
            param_name = "cmd"
        else:
            param_type = f"{use_case.name}Query"
            param_name = "query"

        result_type = f"{use_case.name}Result"
        func_name = cmd.name.replace("-", "_")
        uc_snake = self._to_snake_case(use_case.name)
        ctx_snake = self._to_snake_case(context_name)

        # 构建完整包路径前缀
        pkg_prefix = f"{project_name}." if project_name else ""

        # 生成函数体
        suite = f"use_case = container.{uc_snake}_use_case()\nreturn use_case.execute({param_name})"

        # 生成函数
        func = FunctionSpec.create(
            name=func_name,
            description=cmd.description,
            parameters=[
                VariableSpec.create(name=param_name, type_spec=parse_type_str(param_type)),
            ],
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
            suite=suite,
        )

        return ModuleSpec.create(
            name=func_name,
            functions=[func],
            imports=[
                ImportFromSpec.create(module="__root__", names=["typer"]),
                ImportFromSpec.create(
                    module=f"{pkg_prefix}{ctx_snake}.container",
                    names=["Container"],
                ),
            ],
            extra_code=[
                RawCodeSpec.create("container = Container()"),
            ],
        )

    def _create_cli_init_module(
        self,
        context_name: str,
        function_names: list[str],
        project_name: str = "",
    ) -> ModuleSpec:
        """生成 CLI __init__.py"""
        ctx_snake = self._to_snake_case(context_name)
        pkg_prefix = f"{project_name}." if project_name else ""
        imports: list[ImportFromSpec] = [
            ImportFromSpec.create(module="__root__", names=["typer"]),
        ]
        for func_name in function_names:
            imports.append(
                ImportFromSpec.create(
                    module=f"{pkg_prefix}{ctx_snake}.interfaces.cli.{func_name}",
                    names=[func_name],
                )
            )

        extra_code_lines = [
            f'app = typer.Typer(help="{context_name} CLI")',
        ]
        for func_name in function_names:
            extra_code_lines.append(f'app.command("{func_name}")({func_name})')

        return ModuleSpec.create(
            name="__init__",
            imports=imports,
            extra_code=[RawCodeSpec.create("\n".join(extra_code_lines))],
        )

    def _map_mcp_interface(
        self,
        mcp_spec: Any,
        context_name: str,
        use_case_index: dict[str, UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """生成 MCP 接口包"""
        modules: list[ModuleSpec] = []
        function_names: list[str] = []

        for tool in mcp_spec.tools:
            module = self._map_mcp_tool(tool, context_name, use_case_index, project_name)
            modules.append(module)
            function_names.append(tool.name)

        # 生成 __init__.py
        init_module = self._create_mcp_init_module(context_name, function_names, project_name)
        modules.append(init_module)

        return PackageSpec.create(
            name="mcp",
            modules=modules,
        )

    def _map_mcp_tool(
        self,
        tool: McpToolSpec,
        context_name: str,
        use_case_index: dict[str, UseCaseSpec],
        project_name: str = "",
    ) -> ModuleSpec:
        """生成单个 MCP tool 模块"""
        use_case = use_case_index.get(tool.use_case)
        if not use_case:
            raise ValueError(f"UseCase '{tool.use_case}' not found for MCP tool '{tool.name}'")

        # 确定参数类型
        if use_case.kind == UseCaseKind.COMMAND:
            param_type = f"{use_case.name}Command"
            param_name = "cmd"
        else:
            param_type = f"{use_case.name}Query"
            param_name = "query"

        result_type = f"{use_case.name}Result"
        uc_snake = self._to_snake_case(use_case.name)
        ctx_snake = self._to_snake_case(context_name)

        # 构建完整包路径前缀
        pkg_prefix = f"{project_name}." if project_name else ""

        # 生成函数体
        suite = f"use_case = container.{uc_snake}_use_case()\nreturn use_case.execute({param_name})"

        # 生成函数
        func = FunctionSpec.create(
            name=tool.name,
            description=tool.description,
            parameters=[
                VariableSpec.create(name=param_name, type_spec=parse_type_str(param_type)),
            ],
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
            suite=suite,
        )

        return ModuleSpec.create(
            name=tool.name,
            functions=[func],
            imports=[
                ImportFromSpec.create(
                    module=f"{pkg_prefix}{ctx_snake}.container",
                    names=["Container"],
                ),
            ],
            extra_code=[
                RawCodeSpec.create("container = Container()"),
            ],
        )

    def _create_mcp_init_module(
        self,
        context_name: str,
        function_names: list[str],
        project_name: str = "",
    ) -> ModuleSpec:
        """生成 MCP __init__.py"""
        ctx_snake = self._to_snake_case(context_name)
        pkg_prefix = f"{project_name}." if project_name else ""
        imports: list[ImportFromSpec] = [
            ImportFromSpec.create(module="mcp.server.fastmcp", names=["FastMCP"]),
        ]
        for func_name in function_names:
            imports.append(
                ImportFromSpec.create(
                    module=f"{pkg_prefix}{ctx_snake}.interfaces.mcp.{func_name}",
                    names=[func_name],
                )
            )

        extra_code_lines = [
            f'mcp = FastMCP("{context_name} MCP")',
        ]
        for func_name in function_names:
            extra_code_lines.append(f"mcp.tool()({func_name})")

        return ModuleSpec.create(
            name="__init__",
            imports=imports,
            extra_code=[RawCodeSpec.create("\n".join(extra_code_lines))],
        )

    def _map_http_interface(
        self,
        http_spec: Any,
        context_name: str,
        use_case_index: dict[str, UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """生成 HTTP 接口包"""
        modules: list[ModuleSpec] = []
        module_names: list[str] = []

        for endpoint in http_spec.endpoints:
            module = self._map_http_endpoint(endpoint, context_name, use_case_index, project_name)
            modules.append(module)
            # 使用 use_case 名称生成模块名 (snake_case)
            module_names.append(module.name)

        # 生成 __init__.py
        init_module = self._create_http_init_module(context_name, module_names, project_name)
        modules.append(init_module)

        return PackageSpec.create(
            name="http",
            modules=modules,
        )

    def _map_http_endpoint(
        self,
        endpoint: HttpEndpointSpec,
        context_name: str,
        use_case_index: dict[str, UseCaseSpec],
        project_name: str = "",
    ) -> ModuleSpec:
        """生成单个 HTTP endpoint 模块"""
        use_case = use_case_index.get(endpoint.use_case)
        if not use_case:
            raise ValueError(f"UseCase '{endpoint.use_case}' not found for HTTP endpoint '{endpoint.path}'")

        # 确定参数类型
        if use_case.kind == UseCaseKind.COMMAND:
            param_type = f"{use_case.name}Command"
            param_name = "cmd"
        else:
            param_type = f"{use_case.name}Query"
            param_name = "query"

        result_type = f"{use_case.name}Result"
        uc_snake = self._to_snake_case(use_case.name)
        ctx_snake = self._to_snake_case(context_name)

        # 构建完整包路径前缀
        pkg_prefix = f"{project_name}." if project_name else ""

        # 生成函数名和模块名 (基于 use_case 名称)
        func_name = uc_snake
        decorator = f'router.{endpoint.method.lower()}("{endpoint.path}")'

        # 生成函数体
        suite = f"use_case = container.{uc_snake}_use_case()\nreturn use_case.execute({param_name})"

        # 生成函数
        func = FunctionSpec.create(
            name=func_name,
            description=endpoint.description,
            parameters=[
                VariableSpec.create(name=param_name, type_spec=parse_type_str(param_type)),
            ],
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
            suite=suite,
            decorators=[decorator],
        )

        return ModuleSpec.create(
            name=func_name,
            functions=[func],
            imports=[
                ImportFromSpec.create(module="fastapi", names=["APIRouter"]),
                ImportFromSpec.create(
                    module=f"{pkg_prefix}{ctx_snake}.container",
                    names=["Container"],
                ),
            ],
            extra_code=[
                RawCodeSpec.create("container = Container()"),
                RawCodeSpec.create("router = APIRouter()"),
            ],
        )

    def _create_http_init_module(
        self,
        context_name: str,
        module_names: list[str],
        project_name: str = "",
    ) -> ModuleSpec:
        """生成 HTTP __init__.py"""
        ctx_snake = self._to_snake_case(context_name)
        pkg_prefix = f"{project_name}." if project_name else ""
        imports: list[ImportFromSpec] = [
            ImportFromSpec.create(module="fastapi", names=["APIRouter"]),
        ]
        for module_name in module_names:
            imports.append(
                ImportFromSpec.create(
                    module=f"{pkg_prefix}{ctx_snake}.interfaces.http.{module_name}",
                    names=[f"router as {module_name}_router"],
                )
            )

        extra_code_lines = [
            'app = APIRouter(prefix="/api")',
        ]
        for module_name in module_names:
            extra_code_lines.append(f"app.include_router({module_name}_router)")

        return ModuleSpec.create(
            name="__init__",
            imports=imports,
            extra_code=[RawCodeSpec.create("\n".join(extra_code_lines))],
        )

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert PascalCase to snake_case"""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)