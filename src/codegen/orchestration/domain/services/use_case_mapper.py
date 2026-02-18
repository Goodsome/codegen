from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.data_contract_spec import (
    DataContractSpec,
)
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import (
    FunctionSpec,
)
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.variable_spec import (
    VariableSpec,
)
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str


@dataclass
class UseCaseMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, use_case: UseCaseSpec) -> ModuleSpec:
        classes: list[ClassSpec] = []
        if use_case.kind is UseCaseKind.COMMAND:
            command_name = f"{use_case.name}Command"
            cmd_attributes = self.attribute_mapper.to_variable_specs(
                use_case.command.attributes,
                default_field_flavor=FieldFlavor.DATACLASS,
            )
            command_class = ClassSpec.create(
                name=command_name,
                decorators=["dataclass(frozen=True)"],
                attributes=cmd_attributes,
            )
            # Create param for execute method
            param = VariableSpec.create(
                name="cmd",
                type_spec=parse_type_str(command_name),
            )
            classes.append(command_class)
        elif use_case.kind is UseCaseKind.QUERY:
            query_name = f"{use_case.name}Query"
            query_attributes = self.attribute_mapper.to_variable_specs(
                use_case.query.attributes,
                default_field_flavor=FieldFlavor.DATACLASS,
            )
            query_class = ClassSpec.create(
                name=query_name,
                decorators=["dataclass(frozen=True)"],
                attributes=query_attributes,
            )
            param = VariableSpec.create(
                name="query",
                type_spec=parse_type_str(query_name),
            )
            classes.append(query_class)
        else:
            raise ValueError(f"Unknown use case kind: {use_case.kind}")

        result_name = f"{use_case.name}Result"
        result_attributes = self.attribute_mapper.to_variable_specs(
            use_case.result.attributes,
            default_field_flavor=FieldFlavor.DATACLASS,
        )
        result_class = ClassSpec.create(
            name=f"{use_case.name}Result",
            decorators=["dataclass(frozen=True)"],
            attributes=result_attributes,
        )
        classes.append(result_class)

        uc_attributes = self.attribute_mapper.to_variable_specs(
            use_case.dependencies,
            default_field_flavor=FieldFlavor.DATACLASS,
        )
        execute_method = FunctionSpec.create(
            name="execute",
            parameters=[param],
            return_annotation=parse_type_str(result_name),
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
        return ModuleSpec.create(
            name=use_case.name,
            classes=classes,
        )

    def to_use_case(self, module_spec: ModuleSpec) -> UseCaseSpec:
        kind = "command"

        command = None
        query = None
        result = None
        uc_name = module_spec.name
        uc_deps = []
        for cls in module_spec.classes:
            if cls.name.endswith("Command"):
                kind = "command"
                command_attributes = self.attribute_mapper.to_attributes(cls.attributes)
                command = DataContractSpec(attributes=command_attributes)
            elif cls.name.endswith("Query"):
                kind = "query"
                query_attributes = self.attribute_mapper.to_attributes(cls.attributes)
                query = DataContractSpec(attributes=query_attributes)
            elif cls.name.endswith("Result"):
                result_attributes = self.attribute_mapper.to_attributes(cls.attributes)
                result = DataContractSpec(attributes=result_attributes)
            else:
                uc_name = cls.name
                uc_deps = self.attribute_mapper.to_attributes(cls.attributes)

        return UseCaseSpec.create(
            name=uc_name,
            kind=kind,
            dependencies=uc_deps,
            command=command,
            query=query,
            result=result,
        )
