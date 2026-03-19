import pytest
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.shared.domain.enums import ContainerType


class TestMethodMapper:
    @pytest.fixture
    def mapper(self):
        return MethodMapper()

    # ============ to_function_spec tests ============

    def test_to_function_spec_simple_none_return(self, mapper):
        """简单返回 None 的方法"""
        method = MethodSpec.create(
            name="save",
            inputs=[],
            output=MethodOutput(type="None"),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "None"

    def test_to_function_spec_primitive_return(self, mapper):
        """返回原语类型"""
        method = MethodSpec.create(
            name="get_name",
            inputs=[],
            output=MethodOutput(type="string"),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "str"

    def test_to_function_spec_with_container_list(self, mapper):
        """返回 list 容器类型"""
        method = MethodSpec.create(
            name="get_names",
            inputs=[],
            output=MethodOutput(type="string", container=ContainerType.LIST),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "list[str]"

    def test_to_function_spec_with_container_set(self, mapper):
        """返回 set 容器类型"""
        method = MethodSpec.create(
            name="get_ids",
            inputs=[],
            output=MethodOutput(type="uuid", container=ContainerType.SET),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "set[UUID]"

    def test_to_function_spec_with_container_map(self, mapper):
        """返回 dict 容器类型"""
        method = MethodSpec.create(
            name="get_mapping",
            inputs=[],
            output=MethodOutput(type="integer", container=ContainerType.MAP),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "dict[str, int]"

    def test_to_function_spec_with_optional(self, mapper):
        """返回可选类型"""
        method = MethodSpec.create(
            name="find_by_id",
            inputs=[],
            output=MethodOutput(type="Order", optional=True),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "Order | None"

    def test_to_function_spec_with_optional_list(self, mapper):
        """返回可选的 list 容器类型"""
        method = MethodSpec.create(
            name="get_items",
            inputs=[],
            output=MethodOutput(
                type="string", container=ContainerType.LIST, optional=True
            ),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "list[str] | None"

    def test_to_function_spec_with_custom_type_string(self, mapper):
        """custom_type_string 优先于 type + container"""
        method = MethodSpec.create(
            name="get_complex",
            inputs=[],
            output=MethodOutput(
                type="Any",
                custom_type_string="dict[str, list[int]]",
            ),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "dict[str, list[int]]"

    def test_to_function_spec_with_inputs(self, mapper):
        """带输入参数的方法"""
        method = MethodSpec.create(
            name="process",
            inputs=[
                AttributeSpec.create(name="name", type="string"),
                AttributeSpec.create(name="count", type="integer"),
            ],
            output=MethodOutput(type="boolean"),
        )
        func = mapper.to_function_spec(method)
        assert func.return_annotation.render() == "bool"
        assert len(func.parameters) == 2
        assert func.parameters[0].name == "name"
        assert func.parameters[1].name == "count"

    # ============ to_method tests ============

    def test_to_method_simple_return(self, mapper):
        """从 FunctionSpec 反向构建 MethodOutput - 简单类型"""
        func = FunctionSpec.create(
            name="get_name",
            parameters=[],
            return_annotation=TypeAnnotationSpec(name="str"),
            function_type=FunctionType.FUNCTION,
            suite="...",
        )
        method = mapper.to_method(func)
        assert method.output.type == "string"
        assert method.output.container == ContainerType.NONE
        assert method.output.optional is False
        assert method.output.custom_type_string is None

    def test_to_method_list_return(self, mapper):
        """从 FunctionSpec 反向构建 MethodOutput - list 容器"""
        func = FunctionSpec.create(
            name="get_items",
            parameters=[],
            return_annotation=TypeAnnotationSpec(
                name="list", args=[TypeAnnotationSpec(name="str")]
            ),
            function_type=FunctionType.FUNCTION,
            suite="...",
        )
        method = mapper.to_method(func)
        assert method.output.type == "string"
        assert method.output.container == ContainerType.LIST
        assert method.output.optional is False
        assert method.output.custom_type_string is None

    def test_to_method_optional_return(self, mapper):
        """从 FunctionSpec 反向构建 MethodOutput - 可选类型"""
        func = FunctionSpec.create(
            name="find_by_id",
            parameters=[],
            return_annotation=TypeAnnotationSpec(
                name="Union",
                args=[
                    TypeAnnotationSpec(name="Order"),
                    TypeAnnotationSpec(name="None"),
                ],
            ),
            function_type=FunctionType.FUNCTION,
            suite="...",
        )
        method = mapper.to_method(func)
        assert method.output.type == "Order"
        assert method.output.container == ContainerType.NONE
        assert method.output.optional is True
        assert method.output.custom_type_string is None

    def test_to_method_complex_return_fallback(self, mapper):
        """复杂嵌套类型回退到 custom_type_string"""
        nested = TypeAnnotationSpec(
            name="list", args=[TypeAnnotationSpec(name="int")]
        )
        func = FunctionSpec.create(
            name="get_nested",
            parameters=[],
            return_annotation=TypeAnnotationSpec(name="list", args=[nested]),
            function_type=FunctionType.FUNCTION,
            suite="...",
        )
        method = mapper.to_method(func)
        assert method.output.type == "Any"
        assert method.output.container == ContainerType.NONE
        assert method.output.custom_type_string == "list[list[int]]"

    def test_to_method_skips_self_param(self, mapper):
        """实例方法跳过 self 参数"""
        func = FunctionSpec.create(
            name="get_name",
            parameters=[
                VariableSpec.create(name="self", type_spec=None),
                VariableSpec.create(
                    name="count",
                    type_spec=TypeAnnotationSpec(name="int"),
                ),
            ],
            return_annotation=TypeAnnotationSpec(name="str"),
            function_type=FunctionType.INSTANCE_METHOD,
            suite="...",
        )
        method = mapper.to_method(func)
        assert len(method.inputs) == 1
        assert method.inputs[0].name == "count"

    # ============ roundtrip tests ============

    def test_roundtrip_simple(self, mapper):
        """MethodOutput → FunctionSpec → MethodOutput 双向一致性"""
        original = MethodOutput(type="string")
        method = MethodSpec.create(name="test", inputs=[], output=original)

        func = mapper.to_function_spec(method)
        restored_method = mapper.to_method(func)

        assert restored_method.output.type == original.type
        assert restored_method.output.container == original.container
        assert restored_method.output.optional == original.optional
        assert restored_method.output.custom_type_string == original.custom_type_string

    def test_roundtrip_container_list(self, mapper):
        """list 容器双向一致性"""
        original = MethodOutput(type="integer", container=ContainerType.LIST)
        method = MethodSpec.create(name="test", inputs=[], output=original)

        func = mapper.to_function_spec(method)
        restored_method = mapper.to_method(func)

        assert restored_method.output.type == original.type
        assert restored_method.output.container == original.container
        assert restored_method.output.optional == original.optional

    def test_roundtrip_optional(self, mapper):
        """可选类型双向一致性"""
        original = MethodOutput(type="Order", optional=True)
        method = MethodSpec.create(name="test", inputs=[], output=original)

        func = mapper.to_function_spec(method)
        restored_method = mapper.to_method(func)

        assert restored_method.output.type == original.type
        assert restored_method.output.container == original.container
        assert restored_method.output.optional == original.optional

    def test_roundtrip_optional_list(self, mapper):
        """可选 list 容器双向一致性"""
        original = MethodOutput(
            type="string", container=ContainerType.LIST, optional=True
        )
        method = MethodSpec.create(name="test", inputs=[], output=original)

        func = mapper.to_function_spec(method)
        restored_method = mapper.to_method(func)

        assert restored_method.output.type == original.type
        assert restored_method.output.container == original.container
        assert restored_method.output.optional == original.optional

    # ============ Self type for factory methods tests ============

    def test_to_function_spec_returns_self_when_return_type_matches_class_name(
        self, mapper
    ):
        """当返回类型与类名相同时，应使用 Self 类型"""
        method = MethodSpec.create(
            name="create",
            inputs=[],
            output=MethodOutput(type="Any", custom_type_string="Order"),
        )
        func = mapper.to_function_spec(method, class_name="Order")
        assert func.return_annotation.render() == "Self"

    def test_to_function_spec_returns_self_in_required_types(self, mapper):
        """使用 Self 时，Self 应出现在 required_types 中以触发导入"""
        method = MethodSpec.create(
            name="create",
            inputs=[],
            output=MethodOutput(type="Any", custom_type_string="Order"),
        )
        func = mapper.to_function_spec(method, class_name="Order")
        assert "Self" in func.get_required_types()

    def test_to_function_spec_no_self_when_return_type_differs(self, mapper):
        """当返回类型与类名不同时，不应使用 Self 类型"""
        method = MethodSpec.create(
            name="create",
            inputs=[],
            output=MethodOutput(type="Any", custom_type_string="OtherClass"),
        )
        func = mapper.to_function_spec(method, class_name="Order")
        assert func.return_annotation.render() == "OtherClass"
        assert "Self" not in func.get_required_types()

    def test_to_function_spec_no_self_when_class_name_not_provided(self, mapper):
        """当未提供 class_name 时，不应使用 Self 类型"""
        method = MethodSpec.create(
            name="create",
            inputs=[],
            output=MethodOutput(type="Any", custom_type_string="Order"),
        )
        func = mapper.to_function_spec(method)  # no class_name
        assert func.return_annotation.render() == "Order"
        assert "Self" not in func.get_required_types()

    def test_to_function_spec_self_with_optional_return(self, mapper):
        """可选返回类型也应使用 Self"""
        method = MethodSpec.create(
            name="try_create",
            inputs=[],
            output=MethodOutput(type="Any", custom_type_string="Order", optional=True),
        )
        func = mapper.to_function_spec(method, class_name="Order")
        assert func.return_annotation.render() == "Self | None"
        assert "Self" in func.get_required_types()
