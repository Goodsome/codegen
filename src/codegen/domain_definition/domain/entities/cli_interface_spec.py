from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.value_objects.cli_command_spec import CliCommandSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity


class CliInterfaceSpec(Entity):
    """CLI 接口层规范"""

    commands: list[CliCommandSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        context_name: str,
        use_cases: list[UseCaseSpec],
        project_name: str = "",
    ) -> PackageSpec:
        """将 CliInterfaceSpec 转换为 PackageSpec

        Args:
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for cli package
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        modules: list[ModuleSpec] = []
        function_names: list[str] = []

        for cmd in self.commands:
            use_case = use_case_index.get(cmd.use_case)
            if not use_case:
                raise ValueError(f"UseCase '{cmd.use_case}' not found for CLI command '{cmd.name}'")
            module = cmd.to_module_spec(context_name, use_case, project_name)
            modules.append(module)
            function_names.append(cmd.name.replace(" ", "_").replace("-", "_"))

        # 生成 __init__.py
        init_module = self._create_cli_init_module(context_name, function_names, project_name)
        modules.append(init_module)

        return PackageSpec.create(
            name="cli",
            modules=modules,
        )

    def _create_cli_init_module(
        self,
        context_name: str,
        function_names: list[str],
        project_name: str,
    ) -> ModuleSpec:
        """生成 CLI __init__.py"""
        ctx_snake = str(SnakeString(context_name))
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

    @classmethod
    def from_package_spec(
        cls,
        cli_pkg: PackageSpec,
        use_cases: list[UseCaseSpec],
    ) -> Self:
        """从 PackageSpec 逆向解析为 CliInterfaceSpec

        Args:
            cli_pkg: cli 包的 PackageSpec
            use_cases: UseCase 列表，用于索引

        Returns:
            CliInterfaceSpec
        """
        use_case_index = {uc.name: uc for uc in use_cases}
        commands: list[CliCommandSpec] = []

        for module in cli_pkg.modules:
            if module.name == "__init__":
                continue

            cmd = CliCommandSpec.from_module_spec(module, use_case_index)
            if cmd:
                commands.append(cmd)

        return cls(commands=commands)