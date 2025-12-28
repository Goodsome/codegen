import pytest
from codegen.domain_definition.domain.value_objects.meta_value_object import (
    MetaValueObject,
)
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.python_gen.application.translators.domain_trans import DomainTranslator


def test_should_transform_vo_to_class_spec():
    # Arrange: 仅构造一个小的 VO 定义
    vo = MetaValueObject(
        name="UserEmail",
        description="User email address",
        attributes=[Attribute(name="address", type="str")],
    )
    translator = DomainTranslator()

    # Act: 仅测试这个小的转换函数
    class_spec = translator.translate_value_object(vo)

    # Assert: 验证转换结果
    assert class_spec.name == "UserEmail"
    assert "ValueObject" in class_spec.inheritance
    assert len(class_spec.attributes) == 1
    assert class_spec.attributes[0].name == "address"
