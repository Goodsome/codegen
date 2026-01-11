"""
Kind: ValueObject
Name: ParameterSpec
Description: Represents a parameter in a Python function.
"""

from codegen.shared.domain.value_objects.naming_string import SnakeString
import ast

from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.field_spec import FieldSpec
from pydantic.fields import Field
from codegen.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class ParameterSpec(ValueObject):
    """Represents a parameter in a Python function."""

    name: SnakeString
    annotation: TypeAnnotationSpec
    default: FieldSpec | None = Field(default=None)
    optional: bool = Field(default=False)

    @classmethod
    def create(
        cls,
        name: str,
        annotation: str | TypeAnnotationSpec,
        optional: bool = False,
        default_field_flavor: FieldFlavor | None = None,
    ):
        if isinstance(annotation, str):
            annotation_spec = TypeAnnotationSpec.parse(annotation)
        else:
            annotation_spec = annotation
        if default_field_flavor and optional:
            default = FieldSpec.create_from_annotation(
                annotation_spec,
                flavor=default_field_flavor,
            )
        else:
            default = None
        return cls(
            name=SnakeString(name),
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
        default_field_flavor = None
        if in_pydantic_model:
            default_field_flavor = FieldFlavor.PYDANTIC
        if isinstance(node, ast.AnnAssign):
            optional = node.value is not None
            if isinstance(node.target, ast.Name):

                attributes.append(
                    cls.create(
                        name=node.target.id,
                        annotation=TypeAnnotationSpec.parse_ast(node.annotation),
                        optional=optional,
                        default_field_flavor=default_field_flavor,
                    )
                )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attributes.append(
                        cls.create(
                            name=target.id,
                            annotation=TypeAnnotationSpec(name="Any"),
                            default_field_flavor=default_field_flavor,
                        )
                    )
        return attributes

    def get_required_types(self) -> set[str]:
        types = self.annotation.get_all_referenced_names()
        if isinstance(self.default, FieldSpec):
            types.add(self.default.func_name)
        return types

    def render_default(self) -> str:
        if not self.default:
            return ""
        return self.default.render()
