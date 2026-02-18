import pytest
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.shared.domain.enums import ContainerType


class TestAttributeMapperForward:
    """测试 AttributeSpec → VariableSpec 正向转换"""

    @pytest.fixture
    def mapper(self):
        return AttributeMapper()

    # ============ 原语类型正向转换 ============

    def test_forward_primitive_string(self, mapper):
        attr = AttributeSpec.create(name="name", type="string")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "str"
        # VariableSpec doesn't have optional field, check assignment is None (required)
        assert param.assignment is None

    def test_forward_primitive_integer(self, mapper):
        attr = AttributeSpec.create(name="count", type="integer")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "int"

    def test_forward_primitive_float(self, mapper):
        attr = AttributeSpec.create(name="price", type="float")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "float"

    def test_forward_primitive_boolean(self, mapper):
        attr = AttributeSpec.create(name="active", type="boolean")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "bool"

    def test_forward_primitive_datetime(self, mapper):
        attr = AttributeSpec.create(name="created_at", type="datetime")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "datetime"

    def test_forward_primitive_uuid(self, mapper):
        attr = AttributeSpec.create(name="id", type="uuid")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "UUID"

    def test_forward_primitive_any(self, mapper):
        attr = AttributeSpec.create(name="data", type="any")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "Any"

    # ============ 自定义类型正向转换 ============

    def test_forward_custom_type(self, mapper):
        attr = AttributeSpec.create(name="user", type="User")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "User"

    def test_forward_custom_type_with_namespace(self, mapper):
        attr = AttributeSpec.create(name="item", type="sales.OrderItem")
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "sales.OrderItem"

    # ============ 容器类型正向转换 ============

    def test_forward_list_of_strings(self, mapper):
        attr = AttributeSpec(name="names", type="string", container=ContainerType.LIST)
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "list[str]"

    def test_forward_list_of_integers(self, mapper):
        attr = AttributeSpec(name="ids", type="integer", container=ContainerType.LIST)
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "list[int]"

    def test_forward_set_of_strings(self, mapper):
        attr = AttributeSpec(name="tags", type="string", container=ContainerType.SET)
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "set[str]"

    def test_forward_set_of_custom_type(self, mapper):
        attr = AttributeSpec(name="items", type="Item", container=ContainerType.SET)
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "set[Item]"

    def test_forward_map_of_strings(self, mapper):
        attr = AttributeSpec(
            name="metadata", type="string", container=ContainerType.MAP
        )
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "dict[str, str]"

    def test_forward_map_of_custom_type(self, mapper):
        attr = AttributeSpec(
            name="users_by_id", type="User", container=ContainerType.MAP
        )
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "dict[str, User]"

    # ============ 可选类型正向转换 ============

    def test_forward_optional_primitive(self, mapper):
        attr = AttributeSpec.create(name="nickname", type="string", optional=True)
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "str | None"
        assert param.assignment is not None # Logic sets assignment for optional

    def test_forward_optional_custom_type(self, mapper):
        attr = AttributeSpec.create(name="parent", type="Node", optional=True)
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "Node | None"

    # ============ 容器+可选组合正向转换 ============

    def test_forward_optional_list(self, mapper):
        attr = AttributeSpec(
            name="items", type="string", container=ContainerType.LIST, optional=True
        )
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "list[str] | None"

    def test_forward_optional_set(self, mapper):
        attr = AttributeSpec(
            name="tags", type="integer", container=ContainerType.SET, optional=True
        )
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "set[int] | None"

    def test_forward_optional_map(self, mapper):
        attr = AttributeSpec(
            name="config", type="any", container=ContainerType.MAP, optional=True
        )
        param = mapper.to_variable_spec(attr)
        assert param.type_spec.render() == "dict[str, Any] | None"


class TestAttributeMapperReverse:
    """测试 VariableSpec → AttributeSpec 反向转换"""

    @pytest.fixture
    def mapper(self):
        return AttributeMapper()

    # ============ 原语类型反向转换 ============

    def test_reverse_primitive_string(self, mapper):
        spec = TypeAnnotationSpec(name="str")
        param = VariableSpec.create(name="name", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.NONE
        assert attr.optional is False

    def test_reverse_primitive_integer(self, mapper):
        spec = TypeAnnotationSpec(name="int")
        param = VariableSpec.create(name="count", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "integer"

    def test_reverse_primitive_float(self, mapper):
        spec = TypeAnnotationSpec(name="float")
        param = VariableSpec.create(name="price", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "float"

    def test_reverse_primitive_boolean(self, mapper):
        spec = TypeAnnotationSpec(name="bool")
        param = VariableSpec.create(name="active", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "boolean"

    def test_reverse_primitive_datetime(self, mapper):
        spec = TypeAnnotationSpec(name="datetime")
        param = VariableSpec.create(name="created_at", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "datetime"

    def test_reverse_primitive_uuid(self, mapper):
        spec = TypeAnnotationSpec(name="UUID")
        param = VariableSpec.create(name="id", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "uuid"

    def test_reverse_primitive_any(self, mapper):
        spec = TypeAnnotationSpec(name="Any")
        param = VariableSpec.create(name="data", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "any"

    # ============ 自定义类型反向转换 ============

    def test_reverse_custom_type(self, mapper):
        spec = TypeAnnotationSpec(name="User")
        param = VariableSpec.create(name="user", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "User"
        assert attr.container == ContainerType.NONE

    # ============ 容器类型反向转换 ============

    def test_reverse_list_of_strings(self, mapper):
        spec = TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="str")])
        param = VariableSpec.create(name="names", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.LIST

    def test_reverse_list_of_integers(self, mapper):
        spec = TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="int")])
        param = VariableSpec.create(name="ids", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "integer"
        assert attr.container == ContainerType.LIST

    def test_reverse_set_of_strings(self, mapper):
        spec = TypeAnnotationSpec(name="set", args=[TypeAnnotationSpec(name="str")])
        param = VariableSpec.create(name="tags", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.SET

    def test_reverse_map_of_strings(self, mapper):
        spec = TypeAnnotationSpec(
            name="dict",
            args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name="str")],
        )
        param = VariableSpec.create(name="metadata", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "string"
        assert attr.container == ContainerType.MAP

    def test_reverse_map_of_custom_type(self, mapper):
        spec = TypeAnnotationSpec(
            name="dict",
            args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name="User")],
        )
        param = VariableSpec.create(name="users_by_id", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "User"
        assert attr.container == ContainerType.MAP

    # ============ 可选类型反向转换 ============

    def test_reverse_optional_primitive(self, mapper):
        spec = TypeAnnotationSpec(
            name="Union",
            args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name="None")],
        )
        # For reverse, we rely on type_spec, optional flag on VariableSpec is implicit/absent.
        param = VariableSpec.create(name="nickname", type_spec=spec)
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
        param = VariableSpec.create(name="items", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "integer"
        assert attr.container == ContainerType.LIST
        assert attr.optional is True

    # ============ 错误场景反向转换 ============

    def test_reverse_map_with_non_str_key_fallback(self, mapper):
        """dict[int, str] 应该回退到 custom_type_string"""
        spec = TypeAnnotationSpec(
            name="dict",
            args=[TypeAnnotationSpec(name="int"), TypeAnnotationSpec(name="str")],
        )
        param = VariableSpec.create(name="invalid", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "Any"
        assert attr.custom_type_string == "dict[int, str]"

    def test_reverse_nested_container_fallback(self, mapper):
        """list[list[int]] 应该回退到 custom_type_string"""
        inner_list = TypeAnnotationSpec(
            name="list", args=[TypeAnnotationSpec(name="int")]
        )
        spec = TypeAnnotationSpec(name="list", args=[inner_list])
        param = VariableSpec.create(name="nested", type_spec=spec)
        attr = mapper.to_attribute(param)
        assert attr.type == "Any"
        assert attr.custom_type_string == "list[list[int]]"


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
        params = mapper.to_variable_specs(attrs)
        assert len(params) == 3
        assert params[0].type_spec.render() == "int"
        assert params[1].type_spec.render() == "str"
        assert params[2].type_spec.render() == "str | None"

    def test_reverse_batch_conversion(self, mapper):
        params = [
            VariableSpec.create(name="id", type_spec=TypeAnnotationSpec(name="int")),
            VariableSpec.create(
                name="name", type_spec=TypeAnnotationSpec(name="str")
            ),
        ]
        attrs = mapper.to_attributes(params)
        assert len(attrs) == 2
        assert attrs[0].type == "integer"
        assert attrs[1].type == "string"
