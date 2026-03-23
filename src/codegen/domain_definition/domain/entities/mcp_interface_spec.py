from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str
from codegen.shared.models import Entity


class McpInterfaceSpec(Entity):
    """MCP 接口层规范"""

    tools: list[McpToolSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        context_name: str,
        use_cases: list[UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """将 McpInterfaceSpec 转换为 PackageSpec

        Args:
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for mcp package
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        modules: list[ModuleSpec] = []
        function_names: list[str] = []

        for tool in self.tools:
            module = self._create_mcp_tool_module(tool, context_name, use_case_index, project_name)
            modules.append(module)
            function_names.append(self._sanitize_identifier(tool.name))

        # 生成 __init__.py
        init_module = self._create_mcp_init_module(context_name, function_names, project_name)
        modules.append(init_module)

        return PackageSpec.create(
            name="mcp",
            modules=modules,
        )

    def _create_mcp_tool_module(
        self,
        tool: McpToolSpec,
        context_name: str,
        use_case_index: dict[str, UseCaseSpec],
        project_name: str,
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
            name=self._sanitize_identifier(tool.name),
            description=tool.description,
            parameters=[
                VariableSpec.create(name=param_name, type_spec=parse_type_str(param_type)),
            ],
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
            suite=suite,
        )

        return ModuleSpec.create(
            name=self._sanitize_identifier(tool.name),
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
        project_name: str,
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

    @staticmethod
    def _sanitize_identifier(name: str) -> str:
        """Sanitize a name to be a valid Python identifier."""
        return name.replace(" ", "_").replace("-", "_")

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert PascalCase to snake_case"""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)

    @classmethod
    def from_package_spec(
        cls,
        mcp_pkg: PackageSpec,
        use_cases: list[UseCaseSpec],
    ) -> Self:
        """从 PackageSpec 逆向解析为 McpInterfaceSpec

        Args:
            mcp_pkg: mcp 包的 PackageSpec
            use_cases: UseCase 列表，用于索引

        Returns:
            McpInterfaceSpec
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        tools: list[McpToolSpec] = []

        for module in mcp_pkg.modules:
            if module.name == "__init__":
                continue

            # 从模块名推断 tool 名
            tool_name = str(module.name)

            # 从函数中推断 UseCase
            for func in module.functions:
                use_case_name = cls._infer_use_case_from_suite(func.suite, use_case_index)
                if use_case_name:
                    tools.append(McpToolSpec(
                        name=tool_name,
                        use_case=use_case_name,
                        description=func.suite.split("\n")[0] if func.suite else "",
                    ))
                    break

        return cls(tools=tools)

    @classmethod
    def _infer_use_case_from_suite(
        cls,
        suite: str,
        use_case_index: dict[str, UseCaseSpec],
    ) -> str | None:
        """从函数体推断 UseCase 名称"""
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
