import re
from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.module_assignment_spec import ModuleAssignmentSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import ValueObject


class McpToolSpec(ValueObject):
    """MCP Tool 规范"""

    name: str
    use_case: str
    description: str = Field(default_factory=str)

    def to_module_spec(
        self,
        context_name: str,
        use_case: UseCaseSpec,
        project_name: str = "",
    ) -> ModuleSpec:
        """生成单个 MCP tool 模块

        Args:
            context_name: 上下文名称
            use_case: UseCase 规范
            project_name: 项目名称

        Returns:
            ModuleSpec for MCP tool
        """
        # 确定参数类型
        if use_case.kind == UseCaseKind.COMMAND:
            param_type = f"{use_case.name}Command"
            param_name = "cmd"
        else:
            param_type = f"{use_case.name}Query"
            param_name = "query"

        result_type = f"{use_case.name}Result"
        func_name = self.name.replace(" ", "_").replace("-", "_")
        uc_snake = str(SnakeString(use_case.name))
        ctx_snake = str(SnakeString(context_name))

        # 构建完整包路径前缀
        pkg_prefix = f"{project_name}." if project_name else ""

        # 生成函数体
        suite = f"use_case = container.{uc_snake}_use_case()\nreturn use_case.execute({param_name})"

        # 生成函数
        func = FunctionSpec.create(
            name=func_name,
            description=self.description,
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
                ImportFromSpec.create(
                    module=f"{pkg_prefix}{ctx_snake}.container",
                    names=["Container"],
                ),
            ],
            assignments=[
                ModuleAssignmentSpec.create(
                    name="container",
                    value="Container()",
                ),
            ],
        )

    @classmethod
    def from_module_spec(
        cls,
        module: ModuleSpec,
        use_case_index: dict[str, UseCaseSpec],
    ) -> "McpToolSpec | None":
        """从 ModuleSpec 逆向解析为 McpToolSpec

        Args:
            module: MCP tool 模块
            use_case_index: UseCase 名称索引

        Returns:
            McpToolSpec or None if无法解析
        """
        # 从模块名推断 tool 名
        tool_name = str(module.name)

        # 从函数中推断 UseCase
        for func in module.functions:
            use_case_name = cls._infer_use_case_from_suite(func.suite, use_case_index)
            if use_case_name:
                return cls(
                    name=tool_name,
                    use_case=use_case_name,
                    description=func.suite.split("\n")[0] if func.suite else "",
                )
        return None

    @classmethod
    def _infer_use_case_from_suite(
        cls,
        suite: str,
        use_case_index: dict[str, UseCaseSpec],
    ) -> str | None:
        """从函数体推断 UseCase 名称"""
        pattern = r'container\.(\w+)_use_case\(\)'
        match = re.search(pattern, suite)
        if match:
            method_name = match.group(1)
            # 将 snake_case 转换为 PascalCase
            use_case_name = ''.join(word.capitalize() for word in method_name.split('_'))
            if use_case_name in use_case_index:
                return use_case_name
        return None

    @classmethod
    def tools_to_package_spec(
        cls,
        tools: list["McpToolSpec"],
        context_name: str,
        use_cases: list[UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """将 MCP tool 列表转换为 PackageSpec

        Args:
            tools: MCP tool 列表
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for mcp package
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        modules: list[ModuleSpec] = []

        for tool in tools:
            use_case = use_case_index.get(tool.use_case)
            if not use_case:
                raise ValueError(f"UseCase '{tool.use_case}' not found for MCP tool '{tool.name}'")
            module = tool.to_module_spec(context_name, use_case, project_name)
            modules.append(module)

        return PackageSpec.create(
            name="mcp",
            modules=modules,
        )

    @classmethod
    def tools_from_package_spec(
        cls,
        mcp_pkg: PackageSpec,
        use_cases: list[UseCaseSpec],
    ) -> list[Self]:
        """从 PackageSpec 逆向解析为 MCP tool 列表

        Args:
            mcp_pkg: mcp 包的 PackageSpec
            use_cases: UseCase 列表，用于索引

        Returns:
            list of McpToolSpec
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        tools: list[McpToolSpec] = []

        for module in mcp_pkg.modules:
            if module.name == "__init__":
                continue

            tool = McpToolSpec.from_module_spec(module, use_case_index)
            if tool:
                tools.append(tool)

        return tools