from typing import TYPE_CHECKING

from pydantic import Field

from codegen.domain_definition.domain.value_objects.config_field_spec import ConfigFieldSpec
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity

if TYPE_CHECKING:
    from codegen.domain_definition.domain.entities.bounded_context import BoundedContext


class ConfigSpec(Entity):
    """Specification for a configuration object (AppSettings or ContextSettings)."""

    class_name: PascalString | None = Field(default=None)
    env_prefix: str = Field(default="")
    env_file: str | None = Field(default=None)
    fields: list[ConfigFieldSpec] = Field(default_factory=list)

    def to_class_spec(self, class_name: str | None = None) -> ClassSpec:
        """将 ConfigSpec 转换为 ClassSpec"""
        name = (
            str(self.class_name)
            if self.class_name
            else (class_name or "Settings")
        )
        attributes: list[VariableSpec] = [
            field.to_variable_spec() for field in self.fields
        ]
        if self.env_prefix:
            model_config = self._create_model_config_attribute()
            attributes.insert(0, model_config)
        return ClassSpec.create(
            name=name,
            inheritance=["BaseSettings"],
            attributes=attributes,
        )

    def _create_model_config_attribute(self) -> VariableSpec:
        """创建 model_config 属性"""
        kwargs = {}
        if self.env_prefix:
            kwargs["env_prefix"] = AssignmentSpec.from_literal(self.env_prefix)
        assignment = AssignmentSpec.from_call(
            func_name="SettingsConfigDict",
            kwargs=kwargs,
        )
        return VariableSpec.create(
            name="model_config",
            type_spec=None,
            assignment=assignment,
        )

    def to_module_spec(self, class_name: str | None = None) -> ModuleSpec:
        """将 ConfigSpec 转换为 ModuleSpec"""
        class_spec = self.to_class_spec(class_name)
        imports = [
            ImportFromSpec.create(
                module="pydantic_settings",
                names=["BaseSettings", "SettingsConfigDict"],
            )
        ]
        return ModuleSpec.create(
            name="config",
            classes=[class_spec],
            imports=imports,
        )

    def to_app_config_module(
        self, contexts: list["BoundedContext"]
    ) -> ModuleSpec:
        """创建 AppSettings 模块，包含所有 context 的嵌套配置"""
        app_settings = self.to_class_spec(class_name="AppSettings")

        context_config_fields: list[VariableSpec] = []
        context_imports: list[ImportFromSpec] = []

        for context in contexts:
            if context.config:
                context_class_name = f"{context.name}Settings"
                field_assignment = AssignmentSpec.from_call(
                    func_name="Field",
                    kwargs={
                        "default_factory": AssignmentSpec.from_code(context_class_name)
                    },
                )
                field_var = VariableSpec.create(
                    name=str(SnakeString(str(context.name))),
                    type_spec=None,
                    assignment=field_assignment,
                )
                context_config_fields.append(field_var)
                context_imports.append(
                    ImportFromSpec.create(
                        module=f"..{SnakeString(str(context.name))}.config",
                        names=[context_class_name],
                    )
                )

        app_settings.attributes.extend(context_config_fields)

        imports = [
            ImportFromSpec.create(
                module="pydantic_settings",
                names=["BaseSettings", "SettingsConfigDict"],
            ),
            ImportFromSpec.create(
                module="pydantic",
                names=["Field"],
            ),
        ]
        imports.extend(context_imports)

        return ModuleSpec.create(
            name="config",
            classes=[app_settings],
            imports=imports,
        )
