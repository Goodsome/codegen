from codegen.shared.domain.enums import ContainerType
from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)

# 通用原语类型 -> Python 类型映射表
_PRIMITIVE_MAP: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "float": "float",
    "boolean": "bool",
    "datetime": "datetime",
    "uuid": "UUID",
    "any": "Any",
}

# Python 类型 -> 通用原语类型映射表（反向）
_REVERSE_PRIMITIVE_MAP: dict[str, str] = {
    "str": "string",
    "int": "integer",
    "float": "float",
    "bool": "boolean",
    "datetime": "datetime",
    "UUID": "uuid",
    "Any": "any",
}


class TypeDefinition(ValueObject):
    """类型定义的公共部分，被 AttributeSpec 和 MethodOutput 共同继承。"""

    type: str
    container: ContainerType = Field(default=ContainerType.NONE)
    optional: bool = Field(default_factory=bool)
    custom_type_string: str | None = Field(default=None)

    def to_python_annotation(self) -> TypeAnnotationSpec:
        """将 TypeDefinition 转换为 Python 类型注解"""
        if self.custom_type_string:
            return TypeAnnotationSpec(name=self.custom_type_string)

        python_type_name = _PRIMITIVE_MAP.get(self.type, self.type)
        annotation = self._apply_container(python_type_name)

        if self.optional:
            annotation = self._make_optional(annotation)

        return annotation

    def _apply_container(self, core_type: str) -> TypeAnnotationSpec:
        """根据 container 类型包装核心类型"""
        if self.container == ContainerType.NONE:
            return TypeAnnotationSpec(name=core_type)
        elif self.container == ContainerType.LIST:
            return TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name=core_type)])
        elif self.container == ContainerType.SET:
            return TypeAnnotationSpec(name="set", args=[TypeAnnotationSpec(name=core_type)])
        elif self.container == ContainerType.MAP:
            return TypeAnnotationSpec(
                name="dict",
                args=[TypeAnnotationSpec(name="str"), TypeAnnotationSpec(name=core_type)],
            )
        elif self.container == ContainerType.ITERABLE:
            return TypeAnnotationSpec(name="Iterable", args=[TypeAnnotationSpec(name=core_type)])
        elif self.container == ContainerType.CALLABLE:
            return TypeAnnotationSpec(
                name="Callable",
                args=[TypeAnnotationSpec(name="..."), TypeAnnotationSpec(name=core_type)],
            )
        elif self.container == ContainerType.TYPE:
            return TypeAnnotationSpec(name="type", args=[TypeAnnotationSpec(name=core_type)])
        else:
            return TypeAnnotationSpec(name=core_type)

    def _make_optional(self, annotation: TypeAnnotationSpec) -> TypeAnnotationSpec:
        """将类型包装为可选类型 (Union[T, None])"""
        return TypeAnnotationSpec(
            name="Union", args=[annotation, TypeAnnotationSpec(name="None")]
        )

    @classmethod
    def from_python_annotation(cls, annotation: TypeAnnotationSpec | None) -> "TypeDefinition":
        """从 Python 类型注解逆向解析为 TypeDefinition"""
        if annotation is None:
            return cls(type="Any", container=ContainerType.NONE, optional=False)

        is_optional, core_annotation = cls._extract_optional(annotation)

        try:
            container, core_python_type_name = cls._extract_container_and_type(core_annotation)
        except ValueError:
            return cls(
                type="Any",
                container=ContainerType.NONE,
                optional=is_optional,
                custom_type_string=annotation.render(),
            )

        generic_type = _REVERSE_PRIMITIVE_MAP.get(core_python_type_name, core_python_type_name)
        return cls(type=generic_type, container=container, optional=is_optional)

    @classmethod
    def _extract_optional(cls, annotation: TypeAnnotationSpec) -> tuple[bool, TypeAnnotationSpec]:
        """如果是 Union[T, None] 或 Optional[T] 形式，返回 (True, T)"""
        if annotation.name == "Union":
            non_none_args = [arg for arg in annotation.args if arg.name != "None"]
            if len(non_none_args) == 1 and any(arg.name == "None" for arg in annotation.args):
                return (True, non_none_args[0])

        if annotation.name == "Optional" and len(annotation.args) == 1:
            return (True, annotation.args[0])

        return (False, annotation)

    @classmethod
    def _extract_container_and_type(
        cls, annotation: TypeAnnotationSpec
    ) -> tuple[ContainerType, str]:
        """从 TypeAnnotationSpec 提取容器类型和核心类型名"""
        if not annotation.args:
            return (ContainerType.NONE, annotation.name)

        if annotation.name == "list" and len(annotation.args) == 1:
            inner = annotation.args[0]
            if inner.args:
                raise ValueError(f"Nested containers not supported: {annotation.render()}")
            return (ContainerType.LIST, inner.name)

        if annotation.name == "set" and len(annotation.args) == 1:
            inner = annotation.args[0]
            if inner.args:
                raise ValueError(f"Nested containers not supported: {annotation.render()}")
            return (ContainerType.SET, inner.name)

        if annotation.name == "dict" and len(annotation.args) == 2:
            key_type, value_type = annotation.args[0].name, annotation.args[1].name
            if key_type == "str":
                if annotation.args[1].args:
                    raise ValueError(f"Nested containers not supported: {annotation.render()}")
                return (ContainerType.MAP, value_type)
            raise ValueError(f"dict key type must be 'str': {annotation.render()}")

        if annotation.name in ("Iterable", "Sequence", "Collection", "Iterator") and len(annotation.args) == 1:
            inner = annotation.args[0]
            if inner.args:
                raise ValueError(f"Nested containers not supported: {annotation.render()}")
            return (ContainerType.ITERABLE, inner.name)

        if annotation.name == "Callable":
            if len(annotation.args) == 2:
                return_type = annotation.args[1]
                if return_type.args:
                    raise ValueError(f"Nested containers not supported: {annotation.render()}")
                return (ContainerType.CALLABLE, return_type.name)
            elif len(annotation.args) == 0:
                return (ContainerType.NONE, "Any")

        if annotation.name == "type" and len(annotation.args) == 1:
            inner = annotation.args[0]
            if inner.args:
                raise ValueError(f"Nested containers not supported: {annotation.render()}")
            return (ContainerType.TYPE, inner.name)
        
        if annotation.name == "ClassVar" and len(annotation.args) == 1:
            inner = annotation.args[0]
            if inner.args:
                raise ValueError(f"Nested containers not supported: {annotation.render()}")
            return (ContainerType.CLASS_VAR, inner.name)

        raise ValueError(f"Cannot convert complex type: {annotation.render()}")
