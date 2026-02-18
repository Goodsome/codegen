from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from dataclasses import field

from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)
from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec


@dataclass
class ImplementationMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(
        self,
        implementation: ImplementationSpec,
        port: PortSpec,
    ) -> ModuleSpec:
        methods = [
            self.method_mapper.to_function_spec(
                f, function_type=FunctionType.INSTANCE_METHOD
            )
            for f in port.get_final_operations()
        ]
        methods += [
            self.method_mapper.to_function_spec(
                f,
                function_type=FunctionType.INSTANCE_METHOD,
                is_private=True,
            )
            for f in implementation.private_methods
        ]
        attributes = [
            self.attribute_mapper.to_variable_spec(attr)
            for attr in implementation.attributes
        ]
        class_name = self._get_class_name(implementation)
        class_spec = ClassSpec.create(
            name=class_name,
            decorators=["dataclass"],
            description=implementation.description,
            inheritance=[implementation.implements],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=class_spec.name, classes=[class_spec])

    def to_implementation(
        self, module_spec: ModuleSpec, technology: str
    ) -> ImplementationSpec:
        for cls in module_spec.classes:
            if cls.inheritance:
                attributes = [
                    self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
                ]
                private_methods: list[MethodSpec] = []
                for function in cls.methods:
                    if function.is_init_method():
                        continue
                    if function.is_private:
                        private_methods.append(self.method_mapper.to_method(function))
                return ImplementationSpec.create(
                    name=cls.name,
                    implements=cls.inheritance[0],
                    technology=technology,
                    description=cls.description,
                    attributes=attributes,
                    private_methods=private_methods,
                )
        raise ValueError(f"No Implementation found in module, {module_spec.name}")

    def _get_class_name(self, implementation: ImplementationSpec) -> str:
        if implementation.name:
            return implementation.name
        return PascalString(implementation.technology) + implementation.implements
