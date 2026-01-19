from dataclasses import dataclass
from codegen.domain_definition.domain.value_objects.enum_spec import EnumSpec
from codegen.domain_definition.domain.value_objects.enum_member_spec import (
    EnumMemberSpec,
)
from codegen.python_gen.domain.value_objects.enum_spec import PythonEnumSpec
from codegen.python_gen.domain.value_objects.enum_member_spec import (
    PythonEnumMemberSpec,
)
from typing import Iterable
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec


@dataclass
class EnumMapper:

    def to_python_enum_spec(self, meta_enum: EnumSpec) -> PythonEnumSpec:
        return PythonEnumSpec.create(
            name=meta_enum.name,
            description=meta_enum.description,
            members=[
                PythonEnumMemberSpec(
                    name=member.name, value=member.value, description=member.description
                )
                for member in meta_enum.members
            ],
        )

    def to_enum_spec(self, enum_spec: PythonEnumSpec) -> EnumSpec:
        return EnumSpec(
            name=enum_spec.name,
            description=enum_spec.description,
            members=[
                EnumMemberSpec(
                    name=member.name, value=member.value, description=member.description
                )
                for member in enum_spec.members
            ],
        )

    def to_module_spec(self, enums: Iterable[EnumSpec]) -> ModuleSpec:
        return ModuleSpec(
            name="enums",
            enums=[self.to_python_enum_spec(meta_enum) for meta_enum in enums],
        )

    def to_meta_enums(self, module_spec: ModuleSpec) -> Iterable[EnumSpec]:
        return (self.to_enum_spec(enum_spec) for enum_spec in module_spec.enums)
