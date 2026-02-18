import pytest
from codegen.orchestration.domain.services.type_system_converter import (
    TypeSystemConverter,
)
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.shared.domain.enums import ContainerType


class TestTypeSystemConverter:
    @pytest.fixture
    def converter(self):
        return TypeSystemConverter()

    # ============ to_python_annotation tests ============

    def test_to_python_primitive(self, converter):
        attr = AttributeSpec.create(name="name", type="string")
        annotation = converter.to_python_annotation(attr)
        assert annotation.render() == "str"

    def test_to_python_container_list(self, converter):
        attr = AttributeSpec(name="names", type="string", container=ContainerType.LIST)
        annotation = converter.to_python_annotation(attr)
        assert annotation.render() == "list[str]"

    def test_to_python_optional(self, converter):
        attr = AttributeSpec.create(name="name", type="string", optional=True)
        annotation = converter.to_python_annotation(attr)
        assert annotation.render() == "str | None"

    def test_to_python_optional_list(self, converter):
        attr = AttributeSpec(
            name="names", type="integer", container=ContainerType.LIST, optional=True
        )
        annotation = converter.to_python_annotation(attr)
        assert annotation.render() == "list[int] | None"

    # ============ from_python_annotation tests ============

    def test_from_python_primitive(self, converter):
        spec = TypeAnnotationSpec(name="str")
        generic_type, container, is_optional = converter.from_python_annotation(spec)
        assert generic_type == "string"
        assert container == ContainerType.NONE
        assert is_optional is False

    def test_from_python_container_list(self, converter):
        spec = TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="int")])
        generic_type, container, is_optional = converter.from_python_annotation(spec)
        assert generic_type == "integer"
        assert container == ContainerType.LIST
        assert is_optional is False

    def test_from_python_optional(self, converter):
        spec = TypeAnnotationSpec(
            name="Union",
            args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name="None")],
        )
        generic_type, container, is_optional = converter.from_python_annotation(spec)
        assert generic_type == "string"
        assert container == ContainerType.NONE
        assert is_optional is True

    def test_from_python_optional_list(self, converter):
        spec = TypeAnnotationSpec(
            name="Union",
            args=[
                TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="int")]),
                TypeAnnotationSpec(name="None"),
            ],
        )
        generic_type, container, is_optional = converter.from_python_annotation(spec)
        assert generic_type == "integer"
        assert container == ContainerType.LIST
        assert is_optional is True

    def test_from_python_invalid_nested(self, converter):
        inner_list = TypeAnnotationSpec(
            name="list", args=[TypeAnnotationSpec(name="int")]
        )
        spec = TypeAnnotationSpec(name="list", args=[inner_list])
        with pytest.raises(ValueError, match="Nested containers are not supported"):
            converter.from_python_annotation(spec)

    def test_from_python_invalid_map_key(self, converter):
        spec = TypeAnnotationSpec(
            name="dict",
            args=[TypeAnnotationSpec(name="int"), TypeAnnotationSpec(name="str")],
        )
        with pytest.raises(ValueError, match="dict key type must be 'str'"):
            converter.from_python_annotation(spec)
