from typing import Self

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
from codegen.shared.models import Entity
from pydantic import Field


class UseCaseSpec(Entity):
    """Specification of a use case to be generated."""

    name: PascalString
    kind: UseCaseKind
    input_: DataContractSpec
    result: DataContractSpec
    description: str = Field(default_factory=str)
    dependencies: list[AttributeSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        kind: str | UseCaseKind,
        input_: DataContractSpec,
        result: DataContractSpec,
        dependencies: list[AttributeSpec] | None = None,
        description: str = "",
    ):
        if dependencies is None:
            dependencies = []
        if isinstance(kind, str):
            kind = UseCaseKind(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            dependencies=dependencies,
            description=description,
            input_=input_,
            result=result,
        )

    def to_module_spec(self) -> ModuleSpec:
        """将 UseCaseSpec 转换为 ModuleSpec"""
        classes: list[ClassSpec] = []

        param_name = "cmd" if self.kind == UseCaseKind.COMMAND else "query"
        input_class = self.input_.to_class_spec()
        param = VariableSpec.create(
            name=param_name,
            type_spec=parse_type_str(self.input_.name),
        )
        classes.append(input_class)

        result_class = self.result.to_class_spec()
        classes.append(result_class)

        uc_attributes = [
            attr.to_variable_spec(flavor=FieldFlavor.DATACLASS)
            for attr in self.dependencies
        ]
        execute_method = FunctionSpec.create(
            name="execute",
            parameters=[param],
            return_annotation=parse_type_str(self.result.name),
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
        # 1. Find UseCase class by module name
        uc_name = PascalString(str(module.name))
        uc_class = module.get_class(str(uc_name))

        # 2. Parse dependencies from uc_class attributes
        uc_deps = [
            AttributeSpec.from_variable_spec(attr) for attr in uc_class.attributes
        ]

        # 3. Find execute method
        execute_func = uc_class.get_method("execute")

        # 4. Parse parameter info from execute
        if not execute_func.parameters:
            raise ValueError(f"Execute method has no parameters in UseCase class '{uc_name}'")
        param = execute_func.parameters[1]
        param_name = str(param.name)
        input_type_name = param.type_spec.name if param.type_spec else None

        # 5. Parse return type
        result_type_name = execute_func.return_annotation.name if execute_func.return_annotation else None

        # 6. Determine kind from param name
        kind = UseCaseKind.COMMAND if param_name == "cmd" else UseCaseKind.QUERY

        # 7. Get input and result classes
        if input_type_name is None:
            raise ValueError(f"Execute parameter has no type in UseCase class '{uc_name}'")
        input_class = module.get_class(input_type_name)
        if result_type_name is None:
            raise ValueError(f"Execute return type not found in UseCase class '{uc_name}'")
        result_class = module.get_class(result_type_name)

        # 8. Convert to DataContractSpec
        input_ = DataContractSpec.from_class_spec(input_class)
        result = DataContractSpec.from_class_spec(result_class)

        return cls.create(
            name=str(uc_name),
            kind=kind,
            input_=input_,
            result=result,
            dependencies=uc_deps,
            description=uc_class.description,
        )

    def update_metadata(self, kind: str | UseCaseKind | None = None, description: str | None = None) -> Self:
        if kind is not None:
            if isinstance(kind, str):
                kind = UseCaseKind(kind)
            self.kind = kind
        if description is not None:
            self.description = description
        return self