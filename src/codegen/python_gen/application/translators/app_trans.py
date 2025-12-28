from typing import List

from codegen.domain_definition.domain.value_objects.meta_application import (
    MetaApplication,
)
from codegen.domain_definition.domain.value_objects.meta_use_case import MetaUseCase
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
    FunctionType,
)
from .base import BaseTranslator


class AppTranslator(BaseTranslator):

    def translate_application(self, application: MetaApplication) -> PackageSpec:
        sub_packages = [
            self.translate_use_cases(application.use_cases),
        ]
        return PackageSpec.create(
            name="application",
            sub_packages=sub_packages,
        )

    def translate_use_case(self, use_case: MetaUseCase) -> List[ClassSpec]:
        result: List[ClassSpec] = []
        if use_case.kind == "command":
            command_name = f"{use_case.name}Command"
            command_class = ClassSpec(
                name=command_name,
                decorators=["dataclass(frozen=True)"],
                attributes=self._translate_attributes(use_case.command.attributes),
            )
            param = ParameterSpec(
                name="cmd",
                annotation=TypeAnnotationSpec.parse(command_name),
            )
            result.append(command_class)
        elif use_case.kind == "query":
            query_name = f"{use_case.name}Query"
            query_class = ClassSpec(
                name=query_name,
                decorators=["dataclass(frozen=True)"],
                attributes=self._translate_attributes(use_case.query.attributes),
            )
            param = ParameterSpec(
                name="query",
                annotation=TypeAnnotationSpec.parse(query_name),
            )
            result.append(query_class)
        else:
            raise ValueError(f"Unknown use case kind: {use_case.kind}")

        result_name = f"{use_case.name}Result"
        result_class = ClassSpec(
            name=f"{use_case.name}Result",
            decorators=["dataclass(frozen=True)"],
            attributes=self._translate_attributes(use_case.result.attributes),
        )
        result.append(result_class)

        use_case_class = ClassSpec(
            name=use_case.name,
            description=use_case.description,
            decorators=["dataclass"],
            attributes=self._translate_attributes(use_case.attributes),
            methods=[
                FunctionSpec(
                    name="execute",
                    parameters=[param],
                    return_annotation=TypeAnnotationSpec.parse(result_name),
                    function_type=FunctionType.INSTANCE_METHOD,
                )
            ],
        )
        result.append(use_case_class)
        return result

    def translate_use_cases(self, use_cases: List[MetaUseCase]) -> PackageSpec:
        modules: List[ModuleSpec] = []
        for use_case in use_cases:
            classes = self.translate_use_case(use_case)
            module_spec = ModuleSpec.create(
                name=use_case.name,
                classes=classes,
            )
            modules.append(module_spec)
        return PackageSpec.create(
            name="use_cases",
            modules=modules,
        )
