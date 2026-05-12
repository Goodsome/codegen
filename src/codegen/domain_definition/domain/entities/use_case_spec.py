from __future__ import annotations

from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.core.attribute_spec_list import AttributeSpecList
from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.enums import FieldFlavor, FunctionType
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import (
    parse_type_str,
)
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.domain_definition.domain.entities.dto_spec import DtoSpec
from codegen.shared.domain.core import Entity


class UseCaseSpec(Entity):
    """Specification of a use case to be generated."""

    name: PascalString
    kind: UseCaseKind
    inputs: AttributeSpecList = Field(default_factory=AttributeSpecList)
    outputs: AttributeSpecList = Field(default_factory=AttributeSpecList)
    description: str = Field(default_factory=str)
    dependencies: AttributeSpecList = Field(default_factory=AttributeSpecList)

    @classmethod
    def create(
        cls,
        name: str,
        kind: str | UseCaseKind,
        inputs: list[AttributeSpec] | None = None,
        outputs: list[AttributeSpec] | None = None,
        dependencies: list[AttributeSpec] | None = None,
        description: str = "",
    ):
        if isinstance(kind, str):
            kind = UseCaseKind(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            inputs=AttributeSpecList(root=inputs or []),
            outputs=AttributeSpecList(root=outputs or []),
            dependencies=AttributeSpecList(root=dependencies or []),
            description=description,
        )

    def to_module_spec(self) -> ModuleSpec:
        """将 UseCaseSpec 转换为 ModuleSpec"""
        classes: list[ClassSpec] = []

        param_name = "cmd" if self.kind == UseCaseKind.COMMAND else "query"
        input_class_name = (
            f"{self.name}Command"
            if self.kind == UseCaseKind.COMMAND
            else f"{self.name}Query"
        )
        params = [
            VariableSpec.create(name="self", type_spec=parse_type_str("Self")),
            VariableSpec.create(
                name=param_name,
                type_spec=parse_type_str(input_class_name),
            ),
        ]

        result_class_name = f"{self.name}Result"

        uc_attributes = self.dependencies.to_variable_specs(
            flavor=FieldFlavor.DATACLASS
        )
        execute_method = FunctionSpec.create(
            name="execute",
            parameters=params,
            return_annotation=parse_type_str(result_class_name),
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
    def from_module_spec(cls, module: ModuleSpec) -> UseCaseSpec:
        """将 ModuleSpec 逆向解析为 UseCaseSpec"""
        # 1. Find UseCase class by module name
        uc_name = PascalString(str(module.name))
        uc_class = module.get_class(str(uc_name))

        # 2. Parse dependencies from uc_class attributes
        uc_deps = AttributeSpecList.from_variable_specs(uc_class.attributes)

        # 3. Find execute method
        execute_func = uc_class.get_method("execute")

        # 4. Parse parameter info from execute
        if not execute_func.parameters:
            raise ValueError(
                f"Execute method has no parameters in UseCase class '{uc_name}'"
            )
        param = execute_func.parameters[1]
        param_name = str(param.name)
        input_type_name = param.type_spec.name if param.type_spec else None

        # 5. Parse return type
        result_type_name = (
            execute_func.return_annotation.name
            if execute_func.return_annotation
            else None
        )

        # 6. Determine kind from param name
        kind = UseCaseKind.COMMAND if param_name == "cmd" else UseCaseKind.QUERY

        # 7. Get input and result classes
        if input_type_name is None:
            raise ValueError(
                f"Execute parameter has no type in UseCase class '{uc_name}'"
            )
        input_class = module.get_class_or_none(input_type_name)
        inputs = AttributeSpecList(root=[])
        if input_class:
            inputs = AttributeSpecList.from_variable_specs(input_class.attributes)
            
        if result_type_name is None:
            raise ValueError(
                f"Execute return type not found in UseCase class '{uc_name}'"
            )
        result_class = module.get_class_or_none(result_type_name)
        outputs = AttributeSpecList(root=[])
        if result_class:
            outputs = AttributeSpecList.from_variable_specs(result_class.attributes)

        return cls(
            name=uc_name,
            kind=kind,
            inputs=inputs,
            outputs=outputs,
            dependencies=uc_deps,
            description=uc_class.description,
        )

    def update(
        self, kind: str | UseCaseKind | None = None, description: str | None = None
    ) -> Self:
        """Update scalar metadata fields. Preserves internal structure."""
        if kind is not None:
            if isinstance(kind, str):
                kind = UseCaseKind(kind)
            self.kind = kind
        if description is not None:
            self.description = description
        return self

    def collect_dtos(self: Self) -> list[DtoSpec]:
        """Convert inputs and outputs into DtoSpec instances.

        Returns a list of DtoSpec: {Name}Command/{Name}Query from inputs,
        {Name}Result from outputs.
        """
        if not self.inputs.root and not self.outputs.root:
            return []

        input_dto = self._build_input_dto()
        output_dto = self._build_output_dto()
        return [input_dto, output_dto]

    def _input_dto_name(self: Self) -> PascalString:
        """Derive the input DTO name from use case name and kind."""
        suffix = "Command" if self.kind == UseCaseKind.COMMAND else "Query"
        return PascalString(f"{self.name}{suffix}")

    def _build_input_dto(self: Self) -> DtoSpec:
        """Build input DtoSpec from inputs."""
        return DtoSpec(
            name=self._input_dto_name(),
            description="",
            base_types=["BaseModel"],
            attributes=self.inputs,
        )

    def _build_output_dto(self: Self) -> DtoSpec:
        """Build output DtoSpec from outputs."""
        return DtoSpec(
            name=PascalString(f"{self.name}Result"),
            description="",
            base_types=["BaseModel"],
            attributes=self.outputs,
        )
