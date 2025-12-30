from codegen.orchestration.domain.services.method_mapper import MethodMapper
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.meta_use_case import MetaUseCase
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
    FunctionType,
)
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


@dataclass
class UseCaseMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, use_case: MetaUseCase) -> ModuleSpec:
        classes: list[ClassSpec] = []
        if use_case.kind == "command":
            command_name = f"{use_case.name}Command"
            cmd_attributes = self.attribute_mapper.to_parameter_specs(
                use_case.command.attributes
            )
            command_class = ClassSpec(
                name=command_name,
                decorators=["dataclass(frozen=True)"],
                attributes=cmd_attributes,
            )
            param = ParameterSpec(
                name="cmd",
                annotation=TypeAnnotationSpec.parse(command_name),
            )
            classes.append(command_class)
        elif use_case.kind == "query":
            query_name = f"{use_case.name}Query"
            query_attributes = self.attribute_mapper.to_parameter_specs(
                use_case.query.attributes
            )
            query_class = ClassSpec(
                name=query_name,
                decorators=["dataclass(frozen=True)"],
                attributes=query_attributes,
            )
            param = ParameterSpec(
                name="query",
                annotation=TypeAnnotationSpec.parse(query_name),
            )
            classes.append(query_class)
        else:
            raise ValueError(f"Unknown use case kind: {use_case.kind}")

        result_name = f"{use_case.name}Result"
        result_attributes = self.attribute_mapper.to_parameter_specs(
            use_case.result.attributes
        )
        result_class = ClassSpec(
            name=f"{use_case.name}Result",
            decorators=["dataclass(frozen=True)"],
            attributes=result_attributes,
        )
        classes.append(result_class)

        uc_attributes = self.attribute_mapper.to_parameter_specs(use_case.attributes)
        execute_method = FunctionSpec.create(
            name="execute",
            parameters=[param],
            return_annotation=TypeAnnotationSpec.parse(result_name),
            function_type=FunctionType.INSTANCE_METHOD,
        )
        uc_class = ClassSpec.create(
            name=use_case.name,
            description=use_case.description,
            decorators=["dataclass"],
            attributes=uc_attributes,
            methods=[execute_method],
        )
        classes.append(uc_class)
        return ModuleSpec.create(name=use_case.name, classes=classes)

    def to_use_case(self, module_spec: ModuleSpec) -> MetaUseCase: ...
