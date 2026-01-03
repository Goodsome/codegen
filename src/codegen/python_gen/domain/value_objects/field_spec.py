from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.python_gen.domain.enums import FieldFlavor


class FieldSpec(ValueObject):
    default: str = Field(default="")
    default_factory: str = Field(default="")
    flavor: FieldFlavor = Field(default=FieldFlavor.PYDANTIC)

    @classmethod
    def create_from_annotation(
        cls,
        annotation: TypeAnnotationSpec,
        flavor: FieldFlavor = FieldFlavor.PYDANTIC,
    ) -> "FieldSpec":
        if annotation.is_nullable():
            return cls(
                default="None",
                flavor=flavor,
            )
        return cls(
            default_factory=annotation.name,
            flavor=flavor,
        )

    @property
    def func_name(self):
        return "Field" if self.flavor == FieldFlavor.PYDANTIC else "field"

    def render(self) -> str:
        args: list[str] = []
        if self.default:
            args.append(f"default={self.default}")
        elif self.default_factory:
            args.append(f"default_factory={self.default_factory}")

        return f"{self.func_name}({', '.join(args)})"
