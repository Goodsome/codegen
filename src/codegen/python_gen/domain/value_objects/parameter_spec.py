"""
Kind: ValueObject
Name: ParameterSpec
Description: Represents a parameter in a Python function.
"""

import ast
from pydantic.fields import Field
from codegen.shared.models import ValueObject

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
        annotation: str | TypeAnnotationSpec,
        optional: bool = False,
        in_pydantic_model: bool = False,
    ):
        if isinstance(annotation, str):
            annotation_spec = TypeAnnotationSpec.parse(annotation)
        else:
            annotation_spec = annotation
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

    @classmethod
    def parse_ast(
        cls,
        node: ast.AnnAssign | ast.Assign,
        in_pydantic_model: bool = False,
    ) -> list["ParameterSpec"]:
        """Parses an AST node into a list of ParameterSpec objects."""
        attributes: list[ParameterSpec] = []
        if isinstance(node, ast.AnnAssign):
            optional = node.value is not None
            if isinstance(node.target, ast.Name):
                attributes.append(
                    cls.create(
                        name=node.target.id,
                        annotation=TypeAnnotationSpec.parse_ast(node.annotation),
                        in_pydantic_model=in_pydantic_model,
                        optional=optional,
                    )
                )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attributes.append(
                        cls.create(
                            name=target.id,
                            annotation=TypeAnnotationSpec(name="Any"),
                            in_pydantic_model=in_pydantic_model,
                        )
                    )
        return attributes

    def get_required_types(self) -> set[str]:
        types = self.annotation.get_all_referenced_names()
        if isinstance(self.default, PydanticField):
            types.add("Field")
        return types

    def render_default(self) -> str:
        if not self.default:
            return ""
        return self.default.render()
