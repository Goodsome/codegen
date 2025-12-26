"""
Kind: ValueObject
Name: ParameterSpec
Description: Represents a parameter in a Python function.
"""

from pydantic.fields import Field
from codegen.domain.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class PydanticField(ValueObject):
    default: str = Field(default="")
    default_factory: str = Field(default="")

    @classmethod
    def create_from_annotation(cls, annotation: TypeAnnotationSpec) -> "PydanticField":
        """Parses a Pydantic field annotation into a PydanticField object."""
        if annotation.is_nullable():
            return cls(default="None")
        return cls(default_factory=annotation.name)

    def render(self) -> str:
        if self.default:
            return f"Field(default={self.default})"
        elif self.default_factory:
            return f"Field(default_factory={self.default_factory})"
        else:
            return "Field()"


class ParameterSpec(ValueObject):
    """Represents a parameter in a Python function."""

    name: str
    annotation: TypeAnnotationSpec
    default: PydanticField | None = Field(default=None)
    optional: bool = Field(default=False)

    @classmethod
    def create(
        cls,
        name: str,
        annotation: str,
        optional: bool = False,
        in_pydantic_model: bool = False,
    ):
        annotation_spec = TypeAnnotationSpec.parse(annotation)
        if in_pydantic_model and optional:
            default = PydanticField.create_from_annotation(annotation_spec)
        else:
            default = None
        return cls(
            name=name,
            annotation=annotation_spec,
            default=default,
            optional=optional,
        )

    def get_required_types(self) -> set[str]:
        types = self.annotation.get_all_referenced_names()
        if isinstance(self.default, PydanticField):
            types.add("Field")
        return types

    def render_default(self) -> str:
        if not self.default:
            return ""
        return self.default.render()
