from dataclasses import field
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.meta_implementation import (
    ImplementationSpec,
)
from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.shared.domain.services.naming_service import NamingService


@dataclass
class ImplementationMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)
    naming_service: NamingService = field(default_factory=NamingService)

    def to_module_spec(
        self,
        implementation: ImplementationSpec,
        ports_class_specs: dict[str, ClassSpec],
    ) -> ModuleSpec:
        if implementation.implements not in ports_class_specs:
            raise ValueError(
                f"Could not find port class spec for {implementation.implements}"
            )
        port_cls = ports_class_specs[implementation.implements]
        methods = [self.remove_abstract_method(f) for f in port_cls.methods]
        attributes = [
            self.attribute_mapper.to_parameter_spec(attr)
            for attr in implementation.attributes
        ]
        class_spec = ClassSpec.create(
            name=implementation.to_class_name(),
            description=implementation.description,
            inheritance=[implementation.implements],
            attributes=attributes,
            methods=methods,
        )
        module_name = self.naming_service.to_snake_case(class_spec.name)
        return ModuleSpec.create(name=module_name, classes=[class_spec])

    def to_implementation(
        self, module_spec: ModuleSpec, kind: str, technology: str
    ) -> ImplementationSpec:
        for cls in module_spec.classes:
            if cls.inheritance:
                attributes = [
                    self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
                ]
                return ImplementationSpec.create(
                    implements=cls.inheritance[0],
                    kind=kind,
                    technology=technology,
                    description=cls.description,
                    attributes=attributes,
                )
        raise ValueError("No Implementation found in module")

    def remove_abstract_method(self, function_spec: FunctionSpec) -> FunctionSpec:
        decorators = [d for d in function_spec.decorators if d != "abstractmethod"]
        return FunctionSpec.create(
            name=function_spec.name,
            decorators=decorators,
            parameters=function_spec.parameters,
            suite=function_spec.suite,
            return_annotation=function_spec.return_annotation,
            function_type=function_spec.function_type,
        )
