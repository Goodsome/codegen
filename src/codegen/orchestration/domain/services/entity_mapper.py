from dataclasses import dataclass, field
from typing import Iterable

from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


@dataclass
class EntityMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, entity: EntitySpec) -> ModuleSpec:
        """
        将 EntitySpec 转换为 ModuleSpec。
        生成的类将继承自 'Entity' (来自 codegen.shared.models)。
        """
        # 1. 映射属性 (使用 Pydantic Flavor，因为 Entity 继承自 BaseModel)
        attributes = [
            self.attribute_mapper.to_variable_spec(
                attr,
                default_field_flavor=FieldFlavor.PYDANTIC,
            )
            for attr in entity.attributes
        ]

        # 2. 映射行为方法
        methods = [
            self.method_mapper.to_function_spec(
                method,
                function_type=FunctionType.INSTANCE_METHOD
            )
            for method in entity.behaviors
        ]

        # 3. 创建类规范
        class_spec = ClassSpec.create(
            name=entity.name,
            description=entity.description,
            inheritance=["Entity"],  # 关键点：继承自 Shared Kernel 的 Entity
            attributes=attributes,
            methods=methods,
        )

        return ModuleSpec.create(name=entity.name, classes=[class_spec])

    def to_package_spec(self, entities: Iterable[EntitySpec]) -> PackageSpec:
        """将多个 EntitySpec 转换为一个 'entities' 包"""
        modules = [self.to_module_spec(entity) for entity in entities]
        return PackageSpec.create(
            name="entities",
            modules=modules,
        )

    def to_entity(self, module: ModuleSpec) -> EntitySpec:
        """
        (逆向) 将 ModuleSpec 解析为 EntitySpec。
        """
        # 假设模块中定义的第一个类就是 Entity
        cls = module.classes[0]

        attributes = [
            self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
        ]

        behaviors = [
            self.method_mapper.to_method(method) for method in cls.methods
        ]

        return EntitySpec(
            name=cls.name,
            description=cls.description,
            attributes=attributes,
            behaviors=behaviors,
        )

    def to_entities(self, package: PackageSpec) -> list[EntitySpec]:
        """
        (逆向) 将 'entities' 包解析为 EntitySpec 列表。
        """
        entities: list[EntitySpec] = []
        if package.name != "entities":
            return entities

        for module in package.modules:
            if module.is_init_module():
                continue
            entities.append(self.to_entity(module))

        return entities