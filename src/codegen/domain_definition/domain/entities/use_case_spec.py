from typing import Self

from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers.type_parser import parse_type_str
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity
from pydantic import Field


class UseCaseSpec(Entity):
    """Specification of a use case to be generated."""

    name: PascalString
    kind: UseCaseKind
    inputs: list[AttributeSpec] = Field(default_factory=list)
    outputs: list[AttributeSpec] = Field(default_factory=list)
    description: str = Field(default_factory=str)
    dependencies: list[AttributeSpec] = Field(default_factory=list)

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
        if dependencies is None:
            dependencies = []
        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []
        if isinstance(kind, str):
            kind = UseCaseKind(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            dependencies=dependencies,
            description=description,
            inputs=inputs,
            outputs=outputs,
        )

    def to_module_spec(self) -> ModuleSpec:
        """将 UseCaseSpec 转换为 ModuleSpec"""
        classes: list[ClassSpec] = []

        param_name = "cmd" if self.kind == UseCaseKind.COMMAND else "query"
        input_class_name = f"{self.name}Command" if self.kind == UseCaseKind.COMMAND else f"{self.name}Query"
        input_class = self._build_input_class_spec(input_class_name)
        param = VariableSpec.create(
            name=param_name,
            type_spec=parse_type_str(input_class_name),
        )
        classes.append(input_class)

        result_class_name = f"{self.name}Result"
        result_class = self._build_output_class_spec(result_class_name)
        classes.append(result_class)

        uc_attributes = [
            attr.to_variable_spec(flavor=FieldFlavor.DATACLASS)
            for attr in self.dependencies
        ]
        execute_method = FunctionSpec.create(
            name="execute",
            parameters=[param],
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

    def _build_input_class_spec(self, class_name: str) -> ClassSpec:
        """Build input ClassSpec from inputs list."""
        variable_specs = [
            attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
            for attr in self.inputs
        ]
        return ClassSpec.create(
            name=class_name,
            description="",
            inheritance=["BaseModel"],
            attributes=variable_specs,
        )

    def _build_output_class_spec(self, class_name: str) -> ClassSpec:
        """Build output ClassSpec from outputs list."""
        variable_specs = [
            attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
            for attr in self.outputs
        ]
        return ClassSpec.create(
            name=class_name,
            description="",
            inheritance=["BaseModel"],
            attributes=variable_specs,
        )

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

        # 8. Convert to inputs/outputs directly
        inputs = [AttributeSpec.from_variable_spec(attr) for attr in input_class.attributes]
        outputs = [AttributeSpec.from_variable_spec(attr) for attr in result_class.attributes]

        return cls.create(
            name=str(uc_name),
            kind=kind,
            inputs=inputs,
            outputs=outputs,
            dependencies=uc_deps,
            description=uc_class.description,
        )

    def update(self, kind: str | UseCaseKind | None = None, description: str | None = None) -> Self:
        """Update scalar metadata fields. Preserves internal structure."""
        if kind is not None:
            if isinstance(kind, str):
                kind = UseCaseKind(kind)
            self.kind = kind
        if description is not None:
            self.description = description
        return self

    def add_input(self, input: AttributeSpec) -> Self:
        """Add an AttributeSpec input. Raises ValueError if input with same name exists."""
        for inp in self.inputs:
            if inp.name == input.name:
                raise ValueError(f"Input '{input.name}' already exists in use_case '{self.name}'")
        self.inputs.append(input)
        return self

    def update_input(self, input: AttributeSpec) -> Self:
        """Update an existing AttributeSpec input by name. Raises ValueError if not found."""
        for i, inp in enumerate(self.inputs):
            if inp.name == input.name:
                self.inputs[i] = input
                return self
        raise ValueError(f"Input '{input.name}' not found in use_case '{self.name}'")

    def remove_input(self, name: SnakeString) -> Self:
        """Remove an AttributeSpec input by name. Returns self for chaining."""
        self.inputs = [inp for inp in self.inputs if inp.name != name]
        return self

    def get_input(self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec input by name. Raises ValueError if not found."""
        for inp in self.inputs:
            if inp.name == name:
                return inp
        raise ValueError(f"Input '{name}' not found in use_case '{self.name}'")

    def add_output(self, output: AttributeSpec) -> Self:
        """Add an AttributeSpec output. Raises ValueError if output with same name exists."""
        for out in self.outputs:
            if out.name == output.name:
                raise ValueError(f"Output '{output.name}' already exists in use_case '{self.name}'")
        self.outputs.append(output)
        return self

    def update_output(self, output: AttributeSpec) -> Self:
        """Update an existing AttributeSpec output by name. Raises ValueError if not found."""
        for i, out in enumerate(self.outputs):
            if out.name == output.name:
                self.outputs[i] = output
                return self
        raise ValueError(f"Output '{output.name}' not found in use_case '{self.name}'")

    def remove_output(self, name: SnakeString) -> Self:
        """Remove an AttributeSpec output by name. Returns self for chaining."""
        self.outputs = [out for out in self.outputs if out.name != name]
        return self

    def get_output(self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec output by name. Raises ValueError if not found."""
        for out in self.outputs:
            if out.name == name:
                return out
        raise ValueError(f"Output '{name}' not found in use_case '{self.name}'")

    def add_dependency(self, dependency: AttributeSpec) -> Self:
        """Add an AttributeSpec dependency. Raises ValueError if dependency with same name exists."""
        for dep in self.dependencies:
            if dep.name == dependency.name:
                raise ValueError(f"Dependency '{dependency.name}' already exists in use_case '{self.name}'")
        self.dependencies.append(dependency)
        return self

    def update_dependency(self, dependency: AttributeSpec) -> Self:
        """Update an existing AttributeSpec dependency by name. Raises ValueError if not found."""
        for i, dep in enumerate(self.dependencies):
            if dep.name == dependency.name:
                self.dependencies[i] = dependency
                return self
        raise ValueError(f"Dependency '{dependency.name}' not found in use_case '{self.name}'")

    def remove_dependency(self, name: SnakeString) -> Self:
        """Remove an AttributeSpec dependency by name. Returns self for chaining."""
        self.dependencies = [dep for dep in self.dependencies if dep.name != name]
        return self

    def get_dependency(self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec dependency by name. Raises ValueError if not found."""
        for dep in self.dependencies:
            if dep.name == name:
                return dep
        raise ValueError(f"Dependency '{name}' not found in use_case '{self.name}'")