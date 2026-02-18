from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
)
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from dataclasses import dataclass, field

from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str


@dataclass
class MethodMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)

    def to_function_spec(
        self,
        method: MethodSpec,
        function_type: FunctionType = FunctionType.FUNCTION,
        is_abstract: bool = False,
        is_private: bool = False,
    ) -> FunctionSpec:
        parameters = [
            self.attribute_mapper.to_variable_spec(attr) for attr in method.inputs
        ]
        decorators = []
        if is_abstract:
            decorators.append("abstractmethod")
        if function_type is FunctionType.CLASS_METHOD:
            decorators.append("classmethod")
        elif function_type is FunctionType.STATIC_METHOD:
            decorators.append("staticmethod")
            
        function_name = method.name
        if is_private and not function_name.startswith("_"):
            function_name = "_" + function_name
        return FunctionSpec.create(
            name=function_name,
            parameters=parameters,
            decorators=decorators,
            return_annotation=parse_type_str(method.output.type),
            function_type=function_type,
            suite="...",
            is_private=is_private,
        )

    def to_method(self, function_spec: FunctionSpec) -> MethodSpec:
        inputs: list[AttributeSpec] = []
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
