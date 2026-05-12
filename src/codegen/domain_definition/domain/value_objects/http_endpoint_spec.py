import re
from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_assignment_spec import (
    ModuleAssignmentSpec,
)
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import (
    parse_type_str,
)
from codegen.shared.domain.core import ValueObject
from codegen.shared.domain.value_objects.snake_string import SnakeString


class HttpEndpointSpec(ValueObject):
    """HTTP Endpoint 规范"""

    path: str
    method: str
    use_case: str
    description: str = Field(default_factory=str)

    def to_module_spec(
        self,
        context_name: str,
        use_case: UseCaseSpec,
        project_name: str = "",
    ) -> ModuleSpec:
        """生成单个 HTTP endpoint 模块

        Args:
            context_name: 上下文名称
            use_case: UseCase 规范
            project_name: 项目名称

        Returns:
            ModuleSpec for HTTP endpoint
        """
        param_type = use_case.get_input_name()
        result_type = use_case.get_result_name()
        param_name = "cmd"
        uc_snake = str(SnakeString(use_case.name))
        ctx_snake = str(SnakeString(context_name))

        # 构建完整包路径前缀
        pkg_prefix = f"{project_name}." if project_name else ""

        # 生成函数名和模块名 (基于 use_case 名称)
        func_name = uc_snake
        decorator = f'router.{self.method.lower()}("{self.path}")'

        # 生成函数体
        suite = f"use_case = container.{uc_snake}_use_case()\nreturn use_case.execute({param_name})"

        # 生成函数
        func = FunctionSpec.create(
            name=func_name,
            description=self.description,
            parameters=[
                VariableSpec.create(
                    name=param_name, type_spec=parse_type_str(param_type)
                ),
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
            assignments=[
                ModuleAssignmentSpec.create(
                    name="container",
                    value="Container()",
                ),
                ModuleAssignmentSpec.create(
                    name="router",
                    value="APIRouter()",
                ),
            ],
        )

    @classmethod
    def from_module_spec(
        cls,
        module: ModuleSpec,
        use_case_index: dict[str, UseCaseSpec],
    ) -> Self | None:
        """从 ModuleSpec 逆向解析为 HttpEndpointSpec

        Args:
            module: HTTP endpoint 模块
            use_case_index: UseCase 名称索引

        Returns:
            HttpEndpointSpec or None if无法解析
        """
        # 从函数装饰器推断 path 和 method
        for func in module.functions:
            path, method = cls._parse_route_decorator(func.decorators)
            if path and method:
                use_case_name = cls._infer_use_case_from_suite(
                    func.suite, use_case_index
                )
                if use_case_name:
                    return cls(
                        path=path,
                        method=method,
                        use_case=use_case_name,
                        description=func.suite.split("\n")[0] if func.suite else "",
                    )
        return None

    def update(
        self,
        method: str | None = None,
        use_case: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if method is not None:
            self.method = method
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
    def _parse_route_decorator(
        cls, decorators: list[str]
    ) -> tuple[str | None, str | None]:
        """从装饰器解析路由信息"""
        for decorator in decorators:
            # 匹配 router.get("/path"), router.post("/path") 等
            match = re.match(
                r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)', decorator
            )
            if match:
                method = match.group(1).upper()
                path = match.group(2)
                return path, method
        return None, None

    @classmethod
    def endpoints_to_package_spec(
        cls,
        endpoints: list["HttpEndpointSpec"],
        context_name: str,
        use_cases: list[UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """将 HTTP endpoint 列表转换为 PackageSpec

        Args:
            endpoints: HTTP endpoint 列表
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for http package
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        modules: list[ModuleSpec] = []

        for endpoint in endpoints:
            use_case = use_case_index.get(endpoint.use_case)
            if not use_case:
                raise ValueError(
                    f"UseCase '{endpoint.use_case}' not found for HTTP endpoint '{endpoint.path}'"
                )
            module = endpoint.to_module_spec(context_name, use_case, project_name)
            modules.append(module)

        return PackageSpec.create(
            name="http",
            modules=modules,
        )

    @classmethod
    def endpoints_from_package_spec(
        cls,
        http_pkg: PackageSpec,
        use_cases: list[UseCaseSpec],
    ) -> list[Self]:
        """从 PackageSpec 逆向解析为 HTTP endpoint 列表

        Args:
            http_pkg: http 包的 PackageSpec
            use_cases: UseCase 列表，用于索引

        Returns:
            list of HttpEndpointSpec
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        endpoints: list[HttpEndpointSpec] = []

        for module in http_pkg.modules:
            if module.name == "__init__":
                continue

            endpoint = HttpEndpointSpec.from_module_spec(module, use_case_index)
            if endpoint:
                endpoints.append(endpoint)

        return endpoints
