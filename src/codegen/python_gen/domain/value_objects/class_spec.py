"""
Kind: ValueObject
Name: ClassSpec
Description: Represents a class in a Python module.
"""



from pydantic.fields import Field

from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject


class ClassSpec(ValueObject):
    """Represents a class in a Python module."""

    name: PascalString
    description: str = Field(default="")
    decorators: list[str] = Field(default_factory=list)
    inheritance: list[str] = Field(default_factory=list)
    attributes: list[VariableSpec] = Field(default_factory=list)
    methods: list[FunctionSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        decorators: list[str] | None = None,
        inheritance: list[str] | None = None,
        attributes: list[VariableSpec] | None = None,
        methods: list[FunctionSpec] | None = None,
    ) -> "ClassSpec":
        return cls(
            name=PascalString(name),
            description=description,
            decorators=decorators or [],
            inheritance=inheritance or [],
            attributes=attributes or [],
            methods=methods or [],
        )

    @classmethod
    def create_value_object(cls) -> "ClassSpec":
        return cls._create_base_model("ValueObject")

    @classmethod
    def create_aggregate(cls) -> "ClassSpec":
        return cls._create_base_model("Aggregate")
    
    @classmethod
    def create_entity(cls) -> "ClassSpec":
        return cls._create_base_model("Entity")

    @classmethod
    def create_event(cls) -> "ClassSpec":
        return cls._create_base_model("DomainEvent")
    
    @classmethod
    def _create_base_model(cls, name: str) -> "ClassSpec":
        return cls.create(
            name=name,
            inheritance=["BaseModel"],
        )

    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        types.update(self.inheritance)
        types.update(self.decorators)
        for attribute in self.attributes:
            types.update(attribute.get_required_types())
        for method in self.methods:
            types.update(method.get_required_types())
        return types

    def merge(self, other: "ClassSpec") -> "ClassSpec":
        if self.name != other.name:
            return self
        other_methods = {m.name: m for m in other.methods}
        methods: list[FunctionSpec] = []
        for m in self.methods:
            if m.name in other_methods:
                methods.append(m.merge(other_methods[m.name]))
            else:
                methods.append(m)
        return self.__class__.create(
            name=self.name,
            description=self.description,
            inheritance=self.inheritance,
            decorators=self.decorators,
            attributes=self.attributes,
            methods=methods,
        )
