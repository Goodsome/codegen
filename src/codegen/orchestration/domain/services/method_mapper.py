from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
)
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.enums import FunctionType
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from dataclasses import dataclass, field


@dataclass
class MethodMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)

    def to_function_spec(
        self,
        method: MethodSpec,
        function_type: FunctionType = FunctionType.FUNCTION,
        is_abstract: bool = False,
        is_private: bool = False,
        class_name: str | None = None,
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

        # 使用 TypeSystemConverter 统一转换 MethodOutput → TypeAnnotationSpec
        converter = self.attribute_mapper.type_system_converter

        # Check if return type matches class name for Self type
        return_type = method.output.custom_type_string or method.output.type
        if class_name and return_type == class_name:
            # Use Self type for factory methods returning the same class
            return_annotation = TypeAnnotationSpec(name="Self")
            if method.output.optional:
                return_annotation = TypeAnnotationSpec(
                    name="Union",
                    args=[TypeAnnotationSpec(name="Self"), TypeAnnotationSpec(name="None")],
                )
        else:
            return_annotation = converter.to_python_annotation(method.output)

        return FunctionSpec.create(
            name=function_name,
            parameters=parameters,
            decorators=decorators,
            return_annotation=return_annotation,
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

        # 使用 TypeSystemConverter 从返回注解提取结构化类型信息
        converter = self.attribute_mapper.type_system_converter
        generic_type, container, is_optional, custom_type_string = (
            converter.from_python_annotation(function_spec.return_annotation)
        )

        return MethodSpec(
            name=function_spec.name,
            inputs=inputs,
            output=MethodOutput(
                type=generic_type,
                container=container,
                optional=is_optional,
                custom_type_string=custom_type_string,
            ),
        )
