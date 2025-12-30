from dataclasses import field
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.meta_implementation import (
    MetaImplementation,
)
from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec


@dataclass
class ImplementationMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, implementation: MetaImplementation) -> ModuleSpec:
        attributes = [
            self.attribute_mapper.to_parameter_spec(attr)
            for attr in implementation.attributes
        ]
        class_spec = ClassSpec.create(
            name=implementation.name,
            description=implementation.description,
            inheritance=[implementation.implements],
            attributes=attributes,
        )
        return ModuleSpec.create(name=implementation.name, classes=[class_spec])

    def to_implementation(self, module_spec: ModuleSpec) -> MetaImplementation:
        for cls in module_spec.classes:
            if cls.inheritance:
                attributes = [
                    self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
                ]
                return MetaImplementation(
                    name=cls.name,
                    implements=cls.inheritance[0],
                    description=cls.description,
                    attributes=attributes,
                )
        raise ValueError("No Implementation found in module")
