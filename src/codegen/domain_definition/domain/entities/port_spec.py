from typing import Iterable, Self

from pydantic import Field

from codegen.domain_definition.domain.enums import PortType
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import Entity


class PortSpec(Entity):
    """Specification of a domain port to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    kind: PortType
    aggregate: PascalString | None = None
    operations: list[MethodSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        kind: PortType | str,
        description: str = "",
        aggregate: str | None = None,
        operations: list[MethodSpec] | None = None,
    ) -> "PortSpec":
        if isinstance(kind, str):
            kind = PortType(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            description=description,
            aggregate=aggregate and PascalString(aggregate),
            operations=operations or [],
        )

    def to_module_spec(self) -> ModuleSpec:
        """将 PortSpec 转换为 ModuleSpec"""
        methods = [
            method.to_function_spec(
                type=FunctionType.INSTANCE_METHOD,
                class_name=self.name,
            )
            for method in self.get_final_operations()
        ]
        for method in methods:
            if "abstractmethod" not in method.decorators:
                method.decorators.append("abstractmethod")
        class_spec = ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=["ABC"],
            methods=methods,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def to_package_spec(cls, ports: Iterable[Self]) -> PackageSpec:
        """将多个 PortSpec 转换为一个 'ports' 包"""
        modules = [port.to_module_spec() for port in ports]
        return PackageSpec.create(name="ports", modules=modules)

    @classmethod
    def from_module_spec(cls, module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 PortSpec"""
        cls_spec = module.classes[0]
        operations = [
            MethodSpec.from_function_spec(method) for method in cls_spec.methods
        ]
        if "Repository" in cls_spec.name:
            kind = "repository"
            aggregate = cls_spec.name.replace("Repository", "")
        else:
            kind = "adapter"
            aggregate = None
        return cls.create(
            name=cls_spec.name,
            kind=kind,
            description=cls_spec.description,
            aggregate=aggregate,
            operations=operations,
        )

    @classmethod
    def from_package_spec(cls, package: PackageSpec) -> list[Self]:
        """将 'ports' 包逆向解析为 PortSpec 列表"""
        if package.name != "ports":
            return []
        ports: list[Self] = []
        for module in package.modules:
            if module.is_init_module():
                continue
            ports.append(cls.from_module_spec(module))
        return ports

    def get_final_operations(self) -> list[MethodSpec]:
        default_operations: list[MethodSpec] = self.operations
        if self.kind is not PortType.REPOSITORY:
            return default_operations
        if self.aggregate is None:
            return default_operations
        save_method_spec = self.get_save_method_spec()
        if save_method_spec is not None:
            default_operations.append(save_method_spec)
        delete_method_spec = self.get_delete_method_spec()
        if delete_method_spec is not None:
            default_operations.append(delete_method_spec)
        find_by_id_method_spec = self.get_find_by_id_method_spec()
        if find_by_id_method_spec is not None:
            default_operations.append(find_by_id_method_spec)

        return default_operations

    def get_save_method_spec(self) -> MethodSpec | None:
        for operation in self.operations:
            if operation.name == "save":
                return None
        return MethodSpec.create(
            name="save",
            inputs=[AttributeSpec.create(name=self.aggregate, type=self.aggregate)],
            output=MethodOutput(type="None"),
        )

    def get_delete_method_spec(self) -> MethodSpec | None:
        for operation in self.operations:
            if operation.name == "delete":
                return None
        return MethodSpec.create(
            name="delete",
            inputs=[AttributeSpec.create(name=f"{self.aggregate}_id", type="UUID")],
            output=MethodOutput(type="None"),
        )

    def get_find_by_id_method_spec(self) -> MethodSpec | None:
        for operation in self.operations:
            if operation.name == "find_by_id":
                return None
        return MethodSpec.create(
            name="find_by_id",
            inputs=[AttributeSpec.create(name=f"{self.aggregate}_id", type="UUID")],
            output=MethodOutput(type=f"{self.aggregate} | None"),
        )
