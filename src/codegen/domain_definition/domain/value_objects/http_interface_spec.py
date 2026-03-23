from typing import TYPE_CHECKING

from pydantic import Field

from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import HttpEndpointSpec

if TYPE_CHECKING:
    from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
    from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


class HttpInterfaceSpec(ValueObject):
    """HTTP 接口层规范"""

    endpoints: list[HttpEndpointSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        context_name: str,
        use_cases: list["UseCaseSpec"],
        project_name: str = "",
    ) -> "PackageSpec":
        """将 HttpInterfaceSpec 转换为 PackageSpec

        Args:
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for http package
        """
        from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec

        use_case_index = {uc.name: uc for uc in use_cases}
        modules: list[ModuleSpec] = []
        module_names: list[str] = []

        for endpoint in self.endpoints:
            module = self._create_http_endpoint_module(endpoint, context_name, use_case_index, project_name)
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

    def _create_http_endpoint_module(
        self,
        endpoint: HttpEndpointSpec,
        context_name: str,
        use_case_index: dict[str, "UseCaseSpec"],
        project_name: str,
    ) -> "ModuleSpec":
        """生成单个 HTTP endpoint 模块"""
        from codegen.domain_definition.domain.enums import UseCaseKind
        from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
        from codegen.python_gen.domain.enums import FunctionType
        from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
        from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
        from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
        from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str

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
        project_name: str,
    ) -> "ModuleSpec":
        """生成 HTTP __init__.py"""
        from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
        from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec

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

    @classmethod
    def from_package_spec(
        cls,
        http_pkg: "PackageSpec",
        use_cases: list["UseCaseSpec"],
    ) -> "HttpInterfaceSpec":
        """从 PackageSpec 逆向解析为 HttpInterfaceSpec

        Args:
            http_pkg: http 包的 PackageSpec
            use_cases: UseCase 列表，用于索引

        Returns:
            HttpInterfaceSpec
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        endpoints: list[HttpEndpointSpec] = []

        for module in http_pkg.modules:
            if module.name == "__init__":
                continue

            # 从函数装饰器推断 path 和 method
            for func in module.functions:
                path, method = cls._parse_route_decorator(func.decorators)
                if path and method:
                    use_case_name = cls._infer_use_case_from_suite(func.suite, use_case_index)
                    if use_case_name:
                        endpoints.append(HttpEndpointSpec(
                            path=path,
                            method=method,
                            use_case=use_case_name,
                            description=func.suite.split("\n")[0] if func.suite else "",
                        ))

        return cls(endpoints=endpoints)

    @classmethod
    def _infer_use_case_from_suite(
        cls,
        suite: str,
        use_case_index: dict[str, "UseCaseSpec"],
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

    @classmethod
    def _parse_route_decorator(cls, decorators: list[str]) -> tuple[str | None, str | None]:
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