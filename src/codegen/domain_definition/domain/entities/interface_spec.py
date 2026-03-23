from typing import TYPE_CHECKING

from codegen.shared.models import Entity
from codegen.domain_definition.domain.entities.cli_interface_spec import CliInterfaceSpec
from codegen.domain_definition.domain.entities.mcp_interface_spec import McpInterfaceSpec
from codegen.domain_definition.domain.entities.http_interface_spec import HttpInterfaceSpec

if TYPE_CHECKING:
    from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
    from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


class InterfaceSpec(Entity):
    """接口层总规范"""

    cli: CliInterfaceSpec | None = None
    mcp: McpInterfaceSpec | None = None
    http: HttpInterfaceSpec | None = None

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

        if self.cli:
            cli_pkg = self.cli.to_package_spec(context_name, use_cases, project_name)
            sub_packages.append(cli_pkg)

        if self.mcp:
            mcp_pkg = self.mcp.to_package_spec(context_name, use_cases, project_name)
            sub_packages.append(mcp_pkg)

        if self.http:
            http_pkg = self.http.to_package_spec(context_name, use_cases, project_name)
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
        cli_spec = None
        mcp_spec = None
        http_spec = None

        for sub_pkg in interfaces_pkg.sub_packages:
            if sub_pkg.name == "cli":
                cli_spec = CliInterfaceSpec.from_package_spec(sub_pkg, use_cases)
            elif sub_pkg.name == "mcp":
                mcp_spec = McpInterfaceSpec.from_package_spec(sub_pkg, use_cases)
            elif sub_pkg.name == "http":
                http_spec = HttpInterfaceSpec.from_package_spec(sub_pkg, use_cases)

        return cls(cli=cli_spec, mcp=mcp_spec, http=http_spec)