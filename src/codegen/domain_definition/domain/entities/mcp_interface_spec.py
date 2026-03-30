from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
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
            use_case = use_case_index.get(tool.use_case)
            if not use_case:
                raise ValueError(f"UseCase '{tool.use_case}' not found for MCP tool '{tool.name}'")
            module = tool.to_module_spec(context_name, use_case, project_name)
            modules.append(module)
            function_names.append(tool.name.replace(" ", "_").replace("-", "_"))

        return PackageSpec.create(
            name="mcp",
            modules=modules,
        )

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

            tool = McpToolSpec.from_module_spec(module, use_case_index)
            if tool:
                tools.append(tool)

        return cls(tools=tools)
