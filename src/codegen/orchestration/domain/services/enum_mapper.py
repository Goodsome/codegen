from dataclasses import dataclass
from codegen.domain_definition.domain.value_objects.meta_enum import MetaEnum
from codegen.domain_definition.domain.value_objects.meta_enum_member import (
    MetaEnumMember,
)
from codegen.python_gen.domain.value_objects.enum_spec import EnumSpec
from codegen.python_gen.domain.value_objects.enum_member_spec import EnumMemberSpec
from typing import Iterable
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec


@dataclass
class EnumMapper:

    def to_enum_spec(self, meta_enum: MetaEnum) -> EnumSpec:
        return EnumSpec(
            name=meta_enum.name,
            description=meta_enum.description,
            members=[
                EnumMemberSpec(
                    name=member.name, value=member.value, description=member.description
                )
                for member in meta_enum.members
            ],
        )

    def to_meta_enum(self, enum_spec: EnumSpec) -> MetaEnum:
        return MetaEnum(
            name=enum_spec.name,
            description=enum_spec.description,
            members=[
                MetaEnumMember(
                    name=member.name, value=member.value, description=member.description
                )
                for member in enum_spec.members
            ],
        )

    def to_module_spec(self, enums: Iterable[MetaEnum]) -> ModuleSpec:
        return ModuleSpec(
            name="enums",
            enums=[self.to_enum_spec(meta_enum) for meta_enum in enums],
        )

    def to_meta_enums(self, module_spec: ModuleSpec) -> Iterable[MetaEnum]:
        return (self.to_meta_enum(enum_spec) for enum_spec in module_spec.enums)
