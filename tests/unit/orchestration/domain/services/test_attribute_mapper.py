import pytest
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.shared.domain.enums import ContainerType


class TestAttributeMapperForward:
    """测试 AttributeSpec → ParameterSpec 正向转换"""

    @pytest.fixture
    def mapper(self):
        return AttributeMapper()

    # ============ 原语类型正向转换 ============

    def test_forward_primitive_string(self, mapper):
        attr = AttributeSpec.create(name="name", type="string")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "str"
        assert param.optional is False

    def test_forward_primitive_integer(self, mapper):
        attr = AttributeSpec.create(name="count", type="integer")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "int"

    def test_forward_primitive_float(self, mapper):
        attr = AttributeSpec.create(name="price", type="float")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "float"

    def test_forward_primitive_boolean(self, mapper):
        attr = AttributeSpec.create(name="active", type="boolean")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "bool"

    def test_forward_primitive_datetime(self, mapper):
        attr = AttributeSpec.create(name="created_at", type="datetime")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "datetime"

    def test_forward_primitive_uuid(self, mapper):
        attr = AttributeSpec.create(name="id", type="uuid")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "UUID"

    def test_forward_primitive_any(self, mapper):
        attr = AttributeSpec.create(name="data", type="any")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "Any"

    # ============ 自定义类型正向转换 ============

    def test_forward_custom_type(self, mapper):
        attr = AttributeSpec.create(name="user", type="User")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "User"

    def test_forward_custom_type_with_namespace(self, mapper):
        attr = AttributeSpec.create(name="item", type="sales.OrderItem")
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "sales.OrderItem"

    # ============ 容器类型正向转换 ============

    def test_forward_list_of_strings(self, mapper):
        attr = AttributeSpec(name="names", type="string", container=ContainerType.LIST)
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "list[str]"

    def test_forward_list_of_integers(self, mapper):
        attr = AttributeSpec(name="ids", type="integer", container=ContainerType.LIST)
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "list[int]"

    def test_forward_set_of_strings(self, mapper):
        attr = AttributeSpec(name="tags", type="string", container=ContainerType.SET)
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "set[str]"

    def test_forward_set_of_custom_type(self, mapper):
        attr = AttributeSpec(name="items", type="Item", container=ContainerType.SET)
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "set[Item]"

    def test_forward_map_of_strings(self, mapper):
        attr = AttributeSpec(
            name="metadata", type="string", container=ContainerType.MAP
        )
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "dict[str, str]"

    def test_forward_map_of_custom_type(self, mapper):
        attr = AttributeSpec(
            name="users_by_id", type="User", container=ContainerType.MAP
        )
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "dict[str, User]"

    # ============ 可选类型正向转换 ============

    def test_forward_optional_primitive(self, mapper):
        attr = AttributeSpec.create(name="nickname", type="string", optional=True)
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "str | None"
        assert param.optional is True

    def test_forward_optional_custom_type(self, mapper):
        attr = AttributeSpec.create(name="parent", type="Node", optional=True)
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "Node | None"

    # ============ 容器+可选组合正向转换 ============

    def test_forward_optional_list(self, mapper):
        attr = AttributeSpec(
            name="items", type="string", container=ContainerType.LIST, optional=True
        )
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "list[str] | None"

    def test_forward_optional_set(self, mapper):
        attr = AttributeSpec(
            name="tags", type="integer", container=ContainerType.SET, optional=True
        )
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "set[int] | None"

    def test_forward_optional_map(self, mapper):
        attr = AttributeSpec(
            name="config", type="any", container=ContainerType.MAP, optional=True
        )
        param = mapper.to_parameter_spec(attr)
        assert param.annotation.render() == "dict[str, Any] | None"


class TestAttributeMapperReverse:
    """测试 ParameterSpec → AttributeSpec 反向转换"""

    @pytest.fixture
    def mapper(self):
        return AttributeMapper()

    # ============ 原语类型反向转换 ============

    def test_reverse_primitive_string(self, mapper):
        spec = TypeAnnotationSpec(name="str")
        param = ParameterSpec.create(name="name", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.NONE
        assert attr.optional is False

    def test_reverse_primitive_integer(self, mapper):
        spec = TypeAnnotationSpec(name="int")
        param = ParameterSpec.create(name="count", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "integer"

    def test_reverse_primitive_float(self, mapper):
        spec = TypeAnnotationSpec(name="float")
        param = ParameterSpec.create(name="price", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "float"

    def test_reverse_primitive_boolean(self, mapper):
        spec = TypeAnnotationSpec(name="bool")
        param = ParameterSpec.create(name="active", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "boolean"

    def test_reverse_primitive_datetime(self, mapper):
        spec = TypeAnnotationSpec(name="datetime")
        param = ParameterSpec.create(name="created_at", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "datetime"

    def test_reverse_primitive_uuid(self, mapper):
        spec = TypeAnnotationSpec(name="UUID")
        param = ParameterSpec.create(name="id", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "uuid"

    def test_reverse_primitive_any(self, mapper):
        spec = TypeAnnotationSpec(name="Any")
        param = ParameterSpec.create(name="data", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "any"

    # ============ 自定义类型反向转换 ============

    def test_reverse_custom_type(self, mapper):
        spec = TypeAnnotationSpec(name="User")
        param = ParameterSpec.create(name="user", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "User"
        assert attr.container == ContainerType.NONE

    # ============ 容器类型反向转换 ============

    def test_reverse_list_of_strings(self, mapper):
        spec = TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="str")])
        param = ParameterSpec.create(name="names", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.LIST

    def test_reverse_list_of_integers(self, mapper):
        spec = TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="int")])
        param = ParameterSpec.create(name="ids", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "integer"
        assert attr.container == ContainerType.LIST

    def test_reverse_set_of_strings(self, mapper):
        spec = TypeAnnotationSpec(name="set", args=[TypeAnnotationSpec(name="str")])
        param = ParameterSpec.create(name="tags", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.SET

    def test_reverse_map_of_strings(self, mapper):
        spec = TypeAnnotationSpec(
            name="dict",
            args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name="str")],
        )
        param = ParameterSpec.create(name="metadata", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.MAP

    def test_reverse_map_of_custom_type(self, mapper):
        spec = TypeAnnotationSpec(
            name="dict",
            args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name="User")],
        )
        param = ParameterSpec.create(name="users_by_id", annotation=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "User"
        assert attr.container == ContainerType.MAP

    # ============ 可选类型反向转换 ============

    def test_reverse_optional_primitive(self, mapper):
        spec = TypeAnnotationSpec(
            name="Union",
            args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name="None")],
        )
        param = ParameterSpec.create(name="nickname", annotation=spec, optional=True)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.optional is True

    def test_reverse_optional_list(self, mapper):
        spec = TypeAnnotationSpec(
            name="Union",
            args=[
                TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="int")]),
                TypeAnnotationSpec(name="None"),
            ],
        )
        param = ParameterSpec.create(name="items", annotation=spec, optional=True)
        attr = mapper.to_attribute(param)
        assert attr.type == "integer"
        assert attr.container == ContainerType.LIST
        assert attr.optional is True

    # ============ 错误场景反向转换 ============

    def test_reverse_map_with_non_str_key_raises(self, mapper):
        """dict[int, str] 应该报错，因为 MAP 的键必须是 str"""
        spec = TypeAnnotationSpec(
            name="dict",
            args=[TypeAnnotationSpec(name="int"), TypeAnnotationSpec(name="str")],
        )
        param = ParameterSpec.create(name="invalid", annotation=spec)
        with pytest.raises(ValueError) as exc_info:
            mapper.to_attribute(param)
        assert "str" in str(exc_info.value).lower()

    def test_reverse_nested_container_raises(self, mapper):
        """list[list[int]] 应该报错，因为不支持嵌套容器"""
        inner_list = TypeAnnotationSpec(
            name="list", args=[TypeAnnotationSpec(name="int")]
        )
        spec = TypeAnnotationSpec(name="list", args=[inner_list])
        param = ParameterSpec.create(name="nested", annotation=spec)
        with pytest.raises(ValueError) as exc_info:
            mapper.to_attribute(param)
        assert (
            "nested" in str(exc_info.value).lower()
            or "not supported" in str(exc_info.value).lower()
        )


class TestAttributeMapperBatch:
    """测试批量转换功能"""

    @pytest.fixture
    def mapper(self):
        return AttributeMapper()

    def test_forward_batch_conversion(self, mapper):
        attrs = [
            AttributeSpec.create(name="id", type="integer"),
            AttributeSpec.create(name="name", type="string"),
            AttributeSpec.create(name="tags", type="string", optional=True),
        ]
        params = mapper.to_parameter_specs(attrs)
        assert len(params) == 3
        assert params[0].annotation.render() == "int"
        assert params[1].annotation.render() == "str"
        assert params[2].annotation.render() == "str | None"

    def test_reverse_batch_conversion(self, mapper):
        params = [
            ParameterSpec.create(name="id", annotation=TypeAnnotationSpec(name="int")),
            ParameterSpec.create(
                name="name", annotation=TypeAnnotationSpec(name="str")
            ),
        ]
        attrs = mapper.to_attributes(params)
        assert len(attrs) == 2
        assert attrs[0].type == "integer"
        assert attrs[1].type == "string"
