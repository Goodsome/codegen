from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.value_objects.http_endpoint_spec import HttpEndpointSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity


class HttpInterfaceSpec(Entity):
    """HTTP 接口层规范"""

    endpoints: list[HttpEndpointSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        context_name: str,
        use_cases: list[UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """将 HttpInterfaceSpec 转换为 PackageSpec

        Args:
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for http package
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        modules: list[ModuleSpec] = []
        module_names: list[str] = []

        for endpoint in self.endpoints:
            use_case = use_case_index.get(endpoint.use_case)
            if not use_case:
                raise ValueError(f"UseCase '{endpoint.use_case}' not found for HTTP endpoint '{endpoint.path}'")
            module = endpoint.to_module_spec(context_name, use_case, project_name)
            modules.append(module)
            # 使用 use_case 名称生成模块名 (snake_case)
            module_names.append(module.name)

        return PackageSpec.create(
            name="http",
            modules=modules,
        )

    @classmethod
    def from_package_spec(
        cls,
        http_pkg: PackageSpec,
        use_cases: list[UseCaseSpec],
    ) -> Self:
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

            endpoint = HttpEndpointSpec.from_module_spec(module, use_case_index)
            if endpoint:
                endpoints.append(endpoint)

        return cls(endpoints=endpoints)
