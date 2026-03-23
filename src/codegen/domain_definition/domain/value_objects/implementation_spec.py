from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import ValueObject
from pydantic import Field


class ImplementationSpec(ValueObject):
    """Specification of an implementation to be generated."""

    name: PascalString = Field(default_factory=str)
    implements: PascalString
    technology: SnakeString
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    private_methods: list[MethodSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        implements: str,
        technology: str,
        description: str = "",
        attributes: list[AttributeSpec] | None = None,
        private_methods: list[MethodSpec] | None = None,
    ):
        return cls(
            name=PascalString(name),
            implements=PascalString(implements),
            technology=SnakeString(technology),
            description=description,
            attributes=attributes or [],
            private_methods=private_methods or [],
        )

    def to_module_spec(self, port: PortSpec) -> ModuleSpec:
        """将 ImplementationSpec 转换为 ModuleSpec（需要 port 获取 operations）"""
        methods = [
            f.to_function_spec(type=FunctionType.INSTANCE_METHOD)
            for f in port.get_final_operations()
        ]
        methods += [
            f.to_function_spec(
                type=FunctionType.INSTANCE_METHOD,
                class_name=self._get_class_name(),
            )
            for f in self.private_methods
        ]
        for method in methods[len(port.get_final_operations()):]:
            method.is_private = True

        attributes = [
            attr.to_variable_spec()
            for attr in self.attributes
        ]
        class_name = self._get_class_name()
        class_spec = ClassSpec.create(
            name=class_name,
            decorators=["dataclass"],
            description=self.description,
            inheritance=[self.implements],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=class_name, classes=[class_spec])

    @classmethod
    def from_module_spec(cls, module_spec: ModuleSpec, technology: str) -> "ImplementationSpec":
        """将 ModuleSpec 逆向解析为 ImplementationSpec"""
        for spec_cls in module_spec.classes:
            if spec_cls.inheritance:
                attributes = [
                    AttributeSpec.from_variable_spec(attr) for attr in spec_cls.attributes
                ]
                private_methods: list[MethodSpec] = []
                for function in spec_cls.methods:
                    if function.is_init_method():
                        continue
                    if function.is_private:
                        private_methods.append(MethodSpec.from_function_spec(function))
                return cls.create(
                    name=spec_cls.name,
                    implements=spec_cls.inheritance[0],
                    technology=technology,
                    description=spec_cls.description,
                    attributes=attributes,
                    private_methods=private_methods,
                )
        raise ValueError(f"No Implementation found in module, {module_spec.name}")

    def _get_class_name(self) -> str:
        if self.name:
            return self.name
        return PascalString(self.technology) + self.implements
