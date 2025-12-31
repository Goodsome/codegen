from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
    FunctionType,
)
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from dataclasses import dataclass, field


@dataclass
class MethodMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)

    def to_function_spec(
        self, method: MethodSpec, function_type: FunctionType = FunctionType.FUNCTION
    ) -> FunctionSpec:
        parameters = [
            self.attribute_mapper.to_parameter_spec(attr) for attr in method.inputs
        ]
        return FunctionSpec.create(
            name=method.name,
            parameters=parameters,
            return_annotation=TypeAnnotationSpec.parse(method.output.type),
            function_type=function_type,
            suite="...",
        )

    def to_method(self, function_spec: FunctionSpec) -> MethodSpec:
        inputs: list[Attribute] = []
        for param in function_spec.parameters:
            if (
                function_spec.function_type is FunctionType.INSTANCE_METHOD
                and param.name == "self"
            ):
                continue
            inputs.append(self.attribute_mapper.to_attribute(param))
        return MethodSpec(
            name=function_spec.name,
            inputs=inputs,
            output=MethodOutput(type=function_spec.return_annotation.render()),
        )
