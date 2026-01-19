from dataclasses import field
from typing import Iterable

from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor


@dataclass
class AggregateMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, aggregate: AggregateSpec) -> ModuleSpec:

        attributes = [
            self.attribute_mapper.to_parameter_spec(
                attr,
                default_field_flavor=FieldFlavor.PYDANTIC,
            )
            for attr in aggregate.attributes
        ]
        methods = []
        for method in aggregate.behaviors:
            if method.inputs and method.inputs[0].name == "cls":
                func_type = FunctionType.CLASS_METHOD
            elif method.inputs and method.inputs[0].name == "self":
                func_type = FunctionType.INSTANCE_METHOD
            else:
                func_type = FunctionType.INSTANCE_METHOD
            func_spec = self.method_mapper.to_function_spec(
                method=method,
                function_type=func_type,
            )
            methods.append(func_spec)
        class_spec = ClassSpec.create(
            name=aggregate.name,
            description=aggregate.description,
            inheritance=["Aggregate"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=aggregate.name, classes=[class_spec])

    def to_package_spec(self, aggregates: Iterable[AggregateSpec]) -> PackageSpec:
        modules = [self.to_module_spec(agg) for agg in aggregates]
        return PackageSpec.create(
            name="aggregates",
            modules=modules,
        )

    def to_aggregate(self, module: ModuleSpec) -> AggregateSpec:
        cls = module.classes[0]
        attributes = [
            self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
        ]
        behaviors = [self.method_mapper.to_method(method) for method in cls.methods]
        return AggregateSpec(
            name=cls.name,
            description=cls.description,
            attributes=attributes,
            behaviors=behaviors,
        )

    def to_aggregates(self, package: PackageSpec) -> list[AggregateSpec]:
        aggregates: list[AggregateSpec] = []
        if package.name != "aggregates":
            return aggregates
        for module in package.modules:
            if module.is_init_module():
                continue
            aggregates.append(self.to_aggregate(module))
        return aggregates
