import re
from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.module_assignment_spec import (
    ModuleAssignmentSpec,
)
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import (
    parse_type_str,
)
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.core import ValueObject


class McpToolSpec(ValueObject):
    """MCP Tool 规范"""

    name: SnakeString
    use_case: str
    description: str = Field(default_factory=str)


    def to_module_spec(
        self,
        context_name: str,
        use_case: UseCaseSpec,
    ) -> ModuleSpec:
        """生成单个 CLI 命令模块

        Args:
            context_name: 上下文名称
            use_case: UseCase 规范

        Returns:
            ModuleSpec for CLI command
        """
        # 确定参数类型和属性列表
        if use_case.kind == UseCaseKind.COMMAND:
            param_type_name = f"{use_case.name}Command"
            param_name = "cmd"
        else:
            param_type_name = f"{use_case.name}Query"
            param_name = "query"

        result_type = f"{use_case.name}Result"
        uc_snake = str(SnakeString(use_case.name))
        ctx_snake = str(SnakeString(context_name))

        # 生成 Typer 参数
        parameters: list[VariableSpec] = [
            VariableSpec.create(
                name=param_name,
                type_spec=parse_type_str(param_type_name),
            ),
        ]

        # 生成主函数
        func = FunctionSpec.create(
            name=self.name,
            description=self.description,
            parameters=parameters,
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
        )

        # 生成辅助函数：使用依赖注入
        use_case_type = use_case.name
        provider_path = f"{ctx_snake}.{uc_snake}"
        do_func = FunctionSpec.create(
            name=f"_{uc_snake}",
            parameters=[
                VariableSpec.create(
                    name=param_name,
                    type_spec=parse_type_str(param_type_name),
                ),
                VariableSpec.create(
                    name="use_case",
                    type_spec=parse_type_str(use_case_type),
                    assignment=AssignmentSpec.from_subscript(
                        value=AssignmentSpec.from_symbol("Provide"),
                        slice=AssignmentSpec.from_literal(provider_path),
                    ),
                ),
            ],
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
            suite=f"return use_case.execute({param_name})",
            decorators=["inject"],
        )

        return ModuleSpec.create(
            name=self.name,
            functions=[do_func, func],
            imports=[],
        )

    @classmethod
    def from_module_spec(
        cls,
        module: ModuleSpec,
        use_case_index: dict[str, UseCaseSpec],
    ) -> Self | None:
        """从 ModuleSpec 逆向解析为 CliCommandSpec

        Args:
            module: CLI 命令模块
            use_case_index: UseCase 名称索引

        Returns:
            CliCommandSpec or None if无法解析
        """
        # 从模块名推断命令名
        cmd_name = str(module.name).replace("_", "-")

        # 找到带有 @inject 装饰器的辅助函数，从中提取 use_case 类型
        for func in module.functions:
            if "inject" in func.decorators:
                # 在函数参数中查找 use_case 参数
                for param in func.parameters:
                    if param.name == "use_case" and param.type_spec:
                        use_case_name = param.type_spec.name
                        if use_case_name in use_case_index:
                            return cls(
                                name=cmd_name,
                                use_case=use_case_name,
                                description=func.description or "",
                            )
        return None

    def update(
        self,
        use_case: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if use_case is not None:
            self.use_case = use_case
        if description is not None:
            self.description = description

    @classmethod
    def _infer_use_case_from_suite(
        cls,
        suite: str,
        use_case_index: dict[str, UseCaseSpec],
    ) -> str | None:
        """从函数体推断 UseCase 名称"""
        pattern = r"container\.(\w+)_use_case\(\)"
        match = re.search(pattern, suite)
        if match:
            method_name = match.group(1)
            # 将 snake_case 转换为 PascalCase
            use_case_name = "".join(
                word.capitalize() for word in method_name.split("_")
            )
            if use_case_name in use_case_index:
                return use_case_name
        return None

    @classmethod
    def tools_to_package_spec(
        cls,
        tools: list["McpToolSpec"],
        context_name: str,
        use_cases: list[UseCaseSpec],
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
                raise ValueError(
                    f"UseCase '{tool.use_case}' not found for MCP tool '{tool.name}'"
                )
            module = tool.to_module_spec(context_name, use_case)
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
