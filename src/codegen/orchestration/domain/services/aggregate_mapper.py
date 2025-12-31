from dataclasses import field
from typing import Iterable

from codegen.domain_definition.domain.value_objects.meta_aggregate import MetaAggregate
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionType


@dataclass
class AggregateMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, aggregate: MetaAggregate) -> ModuleSpec:
        from codegen.python_gen.domain.value_objects.parameter_spec import FieldFlavor

        attributes = [
            self.attribute_mapper.to_parameter_spec(
                attr,
                default_field_flavor=FieldFlavor.PYDANTIC,
            )
            for attr in aggregate.attributes
        ]
        methods = [
            self.method_mapper.to_function_spec(
                method, function_type=FunctionType.INSTANCE_METHOD
            )
            for method in aggregate.behaviors
        ]
        class_spec = ClassSpec.create(
            name=aggregate.name,
            description=aggregate.description,
            inheritance=["AggregateRoot"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=aggregate.name, classes=[class_spec])

    def to_package_spec(self, aggregates: Iterable[MetaAggregate]) -> PackageSpec:
        modules = [self.to_module_spec(agg) for agg in aggregates]
        return PackageSpec.create(
            name="aggregates",
            modules=modules,
        )

    def to_aggregate(self, module: ModuleSpec) -> MetaAggregate:
        if len(module.classes) != 1:
            return MetaAggregate(name=module.name)
        cls = module.classes[0]
        attributes = [
            self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
        ]
        behaviors = [self.method_mapper.to_method(method) for method in cls.methods]
        return MetaAggregate(
            name=cls.name,
            description=cls.description,
            attributes=attributes,
            behaviors=behaviors,
        )

    def to_aggregates(self, package: PackageSpec) -> list[MetaAggregate]:
        if package.name != "aggregates":
            return []
        return [self.to_aggregate(module) for module in package.modules]
