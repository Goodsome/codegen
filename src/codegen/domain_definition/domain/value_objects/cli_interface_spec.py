from typing import TYPE_CHECKING

from pydantic import Field

from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.cli_command_spec import CliCommandSpec

if TYPE_CHECKING:
    from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
    from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


class CliInterfaceSpec(ValueObject):
    """CLI 接口层规范"""

    commands: list[CliCommandSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        context_name: str,
        use_cases: list["UseCaseSpec"],
        project_name: str = "",
    ) -> "PackageSpec":
        """将 CliInterfaceSpec 转换为 PackageSpec

        Args:
            context_name: 上下文名称
            use_cases: UseCase 列表，用于解析类型
            project_name: 项目名称

        Returns:
            PackageSpec for cli package
        """
        from codegen.domain_definition.domain.enums import UseCaseKind
        from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
        from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
        from codegen.python_gen.domain.enums import FunctionType
        from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
        from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
        from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
        from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str

        use_case_index = {uc.name: uc for uc in use_cases}
        modules: list[ModuleSpec] = []
        function_names: list[str] = []

        for cmd in self.commands:
            module = self._create_cli_command_module(cmd, context_name, use_case_index, project_name)
            modules.append(module)
            function_names.append(self._sanitize_identifier(cmd.name))

        # 生成 __init__.py
        init_module = self._create_cli_init_module(context_name, function_names, project_name)
        modules.append(init_module)

        return PackageSpec.create(
            name="cli",
            modules=modules,
        )

    def _create_cli_command_module(
        self,
        cmd: CliCommandSpec,
        context_name: str,
        use_case_index: dict[str, "UseCaseSpec"],
        project_name: str,
    ) -> "ModuleSpec":
        """生成单个 CLI 命令模块"""
        from codegen.domain_definition.domain.enums import UseCaseKind
        from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
        from codegen.python_gen.domain.enums import FunctionType
        from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
        from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
        from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
        from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str

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
        func_name = self._sanitize_identifier(cmd.name)
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
        project_name: str,
    ) -> "ModuleSpec":
        """生成 CLI __init__.py"""
        from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
        from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec

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
        cli_pkg: "PackageSpec",
        use_cases: list["UseCaseSpec"],
    ) -> "CliInterfaceSpec":
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

            # 从模块名推断命令名
            cmd_name = str(module.name).replace("_", "-")

            # 从函数中推断 UseCase
            for func in module.functions:
                use_case_name = cls._infer_use_case_from_suite(func.suite, use_case_index)
                if use_case_name:
                    commands.append(CliCommandSpec(
                        name=cmd_name,
                        use_case=use_case_name,
                        description=func.suite.split("\n")[0] if func.suite else "",
                    ))
                    break  # 每个模块只取第一个函数

        return cls(commands=commands)

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