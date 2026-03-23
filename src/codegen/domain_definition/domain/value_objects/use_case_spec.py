from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.data_contract_spec import (
    DataContractSpec,
)
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject
from pydantic import Field


class UseCaseSpec(ValueObject):
    """Specification of a use case to be generated."""

    name: PascalString
    kind: UseCaseKind
    dependencies: list[AttributeSpec] = Field(default_factory=list)
    description: str = Field(default_factory=str)
    command: DataContractSpec = Field(default_factory=DataContractSpec)
    query: DataContractSpec = Field(default_factory=DataContractSpec)
    result: DataContractSpec = Field(default_factory=DataContractSpec)

    @classmethod
    def create(
        cls,
        name: str,
        kind: str | UseCaseKind,
        dependencies: list[AttributeSpec] | None = None,
        description: str = "",
        command: DataContractSpec | None = None,
        query: DataContractSpec | None = None,
        result: DataContractSpec | None = None,
    ):
        if dependencies is None:
            dependencies = []
        if command is None:
            command = DataContractSpec()
        if query is None:
            query = DataContractSpec()
        if result is None:
            result = DataContractSpec()
        if isinstance(kind, str):
            kind = UseCaseKind(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            dependencies=dependencies,
            description=description,
            command=command,
            query=query,
            result=result,
        )

    def to_module_spec(self) -> ModuleSpec:
        """将 UseCaseSpec 转换为 ModuleSpec"""
        classes: list[ClassSpec] = []

        if self.kind is UseCaseKind.COMMAND:
            command_name = f"{self.name}Command"
            cmd_attributes = [
                attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
                for attr in self.command.attributes
            ]
            command_class = ClassSpec.create(
                name=command_name,
                inheritance=["BaseModel"],
                attributes=cmd_attributes,
            )
            param = VariableSpec.create(
                name="cmd",
                type_spec=parse_type_str(command_name),
            )
            classes.append(command_class)
        elif self.kind is UseCaseKind.QUERY:
            query_name = f"{self.name}Query"
            query_attributes = [
                attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
                for attr in self.query.attributes
            ]
            query_class = ClassSpec.create(
                name=query_name,
                inheritance=["BaseModel"],
                attributes=query_attributes,
            )
            param = VariableSpec.create(
                name="query",
                type_spec=parse_type_str(query_name),
            )
            classes.append(query_class)

        result_name = f"{self.name}Result"
        result_attributes = [
            attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
            for attr in self.result.attributes
        ]
        result_class = ClassSpec.create(
            name=result_name,
            inheritance=["BaseModel"],
            attributes=result_attributes,
        )
        classes.append(result_class)

        uc_attributes = [
            attr.to_variable_spec(flavor=FieldFlavor.DATACLASS)
            for attr in self.dependencies
        ]
        execute_method = FunctionSpec.create(
            name="execute",
            parameters=[param],
            return_annotation=parse_type_str(result_name),
            function_type=FunctionType.INSTANCE_METHOD,
        )
        uc_class = ClassSpec.create(
            name=self.name,
            description=self.description,
            decorators=["dataclass"],
            attributes=uc_attributes,
            methods=[execute_method],
        )
        classes.append(uc_class)
        return ModuleSpec.create(name=self.name, classes=classes)

    @classmethod
    def from_module_spec(cls, module: ModuleSpec) -> "UseCaseSpec":
        """将 ModuleSpec 逆向解析为 UseCaseSpec"""
        kind = "command"
        command = None
        query = None
        result = None
        uc_name = module.name
        uc_deps = []

        for spec_cls in module.classes:
            if spec_cls.name.endswith("Command"):
                kind = "command"
                command_attributes = [
                    AttributeSpec.from_variable_spec(attr) for attr in spec_cls.attributes
                ]
                command = DataContractSpec(attributes=command_attributes)
            elif spec_cls.name.endswith("Query"):
                kind = "query"
                query_attributes = [
                    AttributeSpec.from_variable_spec(attr) for attr in spec_cls.attributes
                ]
                query = DataContractSpec(attributes=query_attributes)
            elif spec_cls.name.endswith("Result"):
                result_attributes = [
                    AttributeSpec.from_variable_spec(attr) for attr in spec_cls.attributes
                ]
                result = DataContractSpec(attributes=result_attributes)
            else:
                uc_name = spec_cls.name
                uc_deps = [
                    AttributeSpec.from_variable_spec(attr) for attr in spec_cls.attributes
                ]

        return cls.create(
            name=uc_name,
            kind=kind,
            dependencies=uc_deps,
            command=command,
            query=query,
            result=result,
        )
