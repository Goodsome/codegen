from typing import Iterable

from codegen.domain_definition.domain.value_objects.enum_member_spec import (
    EnumMemberSpec,
)
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.python_enum_member_spec import (
    PythonEnumMemberSpec,
)
from codegen.python_gen.domain.value_objects.python_enum_spec import PythonEnumSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import Entity
from pydantic import Field


class EnumSpec(Entity):
    """Specification of an enum to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    members: list[EnumMemberSpec]

    def to_python_enum_spec(self) -> PythonEnumSpec:
        """将 EnumSpec 转换为 PythonEnumSpec"""
        return PythonEnumSpec.create(
            name=self.name,
            description=self.description,
            members=[
                PythonEnumMemberSpec(
                    name=member.name, value=member.value, description=member.description
                )
                for member in self.members
            ],
        )

    @classmethod
    def from_python_enum_spec(cls, enum_spec: PythonEnumSpec) -> "EnumSpec":
        """将 PythonEnumSpec 逆向解析为 EnumSpec"""
        return cls(
            name=enum_spec.name,
            description=enum_spec.description,
            members=[
                EnumMemberSpec(
                    name=member.name, value=member.value, description=member.description
                )
                for member in enum_spec.members
            ],
        )

    @classmethod
    def to_module_spec(cls, enums: Iterable["EnumSpec"]) -> ModuleSpec:
        """将多个 EnumSpec 转换为一个 'enums' ModuleSpec"""
        return ModuleSpec(
            name="enums",
            enums=[enum.to_python_enum_spec() for enum in enums],
        )

    @classmethod
    def from_module_spec(cls, module_spec: ModuleSpec) -> list["EnumSpec"]:
        """将 ModuleSpec 逆向解析为 EnumSpec 列表"""
        return [cls.from_python_enum_spec(enum_spec) for enum_spec in module_spec.enums]

