from pydantic import Field

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str
from codegen.shared.domain.value_objects.kebab_string import KebabString
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import ValueObject


class CliCommandSpec(ValueObject):
    """CLI 命令规范"""

    name: KebabString
    use_case: PascalString
    description: str = Field(default_factory=str)

    def to_module_spec(
        self,
        context_name: str,
        use_case: UseCaseSpec,
        project_name: str = "",
    ) -> ModuleSpec:
        """生成单个 CLI 命令模块

        Args:
            context_name: 上下文名称
            use_case: UseCase 规范
            project_name: 项目名称

        Returns:
            ModuleSpec for CLI command
        """
        # 确定参数类型和属性列表
        if use_case.kind == UseCaseKind.COMMAND:
            attributes = use_case.command.attributes
            param_type_name = f"{use_case.name}Command"
        else:
            attributes = use_case.query.attributes
            param_type_name = f"{use_case.name}Query"

        result_type = f"{use_case.name}Result"
        func_name = self.name.replace(" ", "_").replace("-", "_")
        uc_snake = str(SnakeString(use_case.name))
        ctx_snake = str(SnakeString(context_name))

        # 生成 Typer 参数
        parameters: list[VariableSpec] = []
        used_short_flags: set[str] = set()

        def get_short_flag(param_name: KebabString) -> str:
            """生成短标志，按'-'分割取首字母拼接，重复则加数字后缀"""
            parts = str(param_name).split("-")
            base_chars = "".join(p[0].lower() for p in parts if p)
            short_flag = f"-{base_chars}"
            suffix = 2
            while short_flag in used_short_flags:
                short_flag = f"-{base_chars}{suffix}"
                suffix += 1
            used_short_flags.add(short_flag)
            return short_flag

        def build_help_kwargs(description: str | None) -> dict[str, AssignmentSpec]:
            """构建 help 参数"""
            if description:
                return {"help": AssignmentSpec.from_literal(description)}
            return {}

        for attr in attributes:
            param_name = KebabString(attr.name)
            type_annotation = attr.to_python_annotation()
            help_kwargs = build_help_kwargs(attr.description)

            if attr.default is None and not attr.optional:
                # 必选参数: Annotated[type, typer.Argument(...)]
                default_assignment = AssignmentSpec.from_literal(None)
                assignment = AssignmentSpec.from_call(
                    "typer.Argument",
                    kwargs=help_kwargs,
                )
            else:
                # 可选参数: Annotated[type, typer.Option(default, --flag, -f, help=...)]
                default_assignment = AssignmentSpec.from_literal(
                    None if attr.default is None else attr.default
                )
                long_flag = f"--{str(param_name)}"
                short_flag = get_short_flag(param_name)
                # typer.Option(default, "--flag", "-f", help="...")
                # flags are positional args, help is kwarg
                option_args = [
                    AssignmentSpec.from_literal(long_flag),
                    AssignmentSpec.from_literal(short_flag),
                ]
                assignment = AssignmentSpec.from_call(
                    "typer.Option",
                    args=option_args,
                    kwargs=help_kwargs,
                )

            annotated_type = TypeAnnotationSpec(
                name="Annotated",
                args=[type_annotation, assignment],
            )
            parameters.append(
                VariableSpec.create(
                    name=param_name, 
                    type_spec=annotated_type,
                    assignment=default_assignment,
                )
            )

        # 生成主函数
        func = FunctionSpec.create(
            name=func_name,
            description=self.description,
            parameters=parameters,
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
        )

        # 生成辅助函数：使用依赖注入
        use_case_type = use_case.name
        provider_path = f"{ctx_snake}_container.{uc_snake}_use_case"
        do_func = FunctionSpec.create(
            name=f"_{uc_snake}",
            parameters=[
                VariableSpec.create(
                    name="cmd",
                    type_spec=parse_type_str(param_type_name),
                ),
                VariableSpec.create(
                    name="use_case",
                    type_spec=parse_type_str(use_case_type),
                    assignment=AssignmentSpec.from_subscript(
                        value=AssignmentSpec.from_symbol("Provide"),
                        slice=AssignmentSpec.from_literal(provider_path)
                    )
                ),
            ],
            return_annotation=parse_type_str(result_type),
            function_type=FunctionType.FUNCTION,
            suite="return use_case.execute(cmd)",
            decorators=["inject"]
        )

        return ModuleSpec.create(
            name=func_name,
            functions=[do_func, func],
            imports=[
                ImportFromSpec.create(module="__root__", names=["typer"]),
            ],
        )

    @classmethod
    def from_module_spec(
        cls,
        module: ModuleSpec,
        use_case_index: dict[str, UseCaseSpec],
    ) -> "CliCommandSpec | None":
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

