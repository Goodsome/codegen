from dataclasses import dataclass
from typing import List, Optional
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
    FunctionType,
)
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


@dataclass
class TranslationContext:
    """翻译上下文，包含命名策略和项目配置"""

    # 目前先留空，后续根据需要添加
    pass


@dataclass
class BaseTranslator:

    def _translate_attribute(
        self, attribute: Attribute, in_pydantic_model: bool
    ) -> ParameterSpec:
        return ParameterSpec.create(
            name=attribute.name,
            annotation=attribute.type,
            optional=attribute.optional,
            in_pydantic_model=in_pydantic_model,
        )

    def _translate_attributes(
        self, attributes: List[Attribute], in_pydantic_model: bool = False
    ) -> List[ParameterSpec]:
        return [self._translate_attribute(a, in_pydantic_model) for a in attributes]

    def _translate_method(
        self, method_spec: MethodSpec, is_abstract: bool = False
    ) -> FunctionSpec:
        parameter_specs = self._translate_attributes(
            method_spec.inputs, in_pydantic_model=False
        )
        if is_abstract:
            decorators = ["abstractmethod"]
        else:
            decorators = []
        return FunctionSpec(
            name=method_spec.name,
            decorators=decorators,
            parameters=parameter_specs,
            return_annotation=TypeAnnotationSpec.parse(method_spec.output.type),
            function_type=FunctionType.INSTANCE_METHOD,
        )

    def _translate_methods(
        self, method_specs: List[MethodSpec], is_abstract: bool = False
    ) -> List[FunctionSpec]:
        return [self._translate_method(m, is_abstract) for m in method_specs]
