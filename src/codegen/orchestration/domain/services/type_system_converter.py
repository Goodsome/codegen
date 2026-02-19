"""
Kind: Service
Name: TypeSystemConverter
Description: 通用类型系统与 Python 类型系统的双向转换器
"""

from dataclasses import dataclass

from codegen.domain_definition.domain.value_objects.attribute_spec import (
    AttributeSpec,
)
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.shared.domain.enums import ContainerType


# 通用原语类型 -> Python 类型映射表
PRIMITIVE_MAP: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "float": "float",
    "boolean": "bool",
    "datetime": "datetime",
    "uuid": "UUID",
    "any": "Any",
}

# Python 类型 -> 通用原语类型映射表（反向）
REVERSE_PRIMITIVE_MAP: dict[str, str] = {
    "str": "string",
    "int": "integer",
    "float": "float",
    "bool": "boolean",
    "datetime": "datetime",
    "UUID": "uuid",
    "Any": "any",
}


@dataclass
class TypeSystemConverter:
    """通用类型系统与 Python 类型系统的双向转换器"""

    def to_python_annotation(self, attribute: AttributeSpec) -> TypeAnnotationSpec:
        """将 AttributeSpec 转换为 TypeAnnotationSpec"""
        # 步骤 0: 检查 custom_type_string
        if attribute.custom_type_string:
            return TypeAnnotationSpec(name=attribute.custom_type_string)

        # 步骤 1: 映射核心类型名称
        python_type_name = PRIMITIVE_MAP.get(attribute.type, attribute.type)

        # 步骤 2: 根据 container 包装类型
        annotation = self._apply_container(python_type_name, attribute.container)

        # 步骤 3: 如果是可选类型，包装为 Union
        if attribute.optional:
            annotation = self._make_optional(annotation)

        return annotation

    def from_python_annotation(
        self, annotation: TypeAnnotationSpec | None
    ) -> tuple[str, ContainerType, bool, str | None]:
        """从 TypeAnnotationSpec 提取 container、core_type 和 optional"""
        if annotation is None:
            return "Any", ContainerType.NONE, False, None

        # 步骤 1: 检查可选类型（Union 且包含 None）
        is_optional, core_annotation = self._extract_optional(annotation)

        # 步骤 2: 从 TypeAnnotationSpec 提取 container 和核心类型
        try:
            container, core_python_type_name = self._extract_container_and_type(
                core_annotation
            )
        except ValueError:
            # 解析失败，回退到 custom_type_string
            return "Any", ContainerType.NONE, is_optional, annotation.render()

        # 步骤 3: 将 Python 类型名反向映射为通用类型名
        generic_type = REVERSE_PRIMITIVE_MAP.get(
            core_python_type_name, core_python_type_name
        )

        return generic_type, container, is_optional, None

    def _apply_container(
        self, core_type: str, container: ContainerType
    ) -> TypeAnnotationSpec:
        """根据 container 类型包装核心类型"""
        if container == ContainerType.NONE:
            return TypeAnnotationSpec(name=core_type)

        elif container == ContainerType.LIST:
            return TypeAnnotationSpec(
                name="list", args=[TypeAnnotationSpec(name=core_type)]
            )

        elif container == ContainerType.SET:
            return TypeAnnotationSpec(
                name="set", args=[TypeAnnotationSpec(name=core_type)]
            )

        elif container == ContainerType.MAP:
            return TypeAnnotationSpec(
                name="dict",
                args=[
                    TypeAnnotationSpec(name="str"),  # 键固定为 str
                    TypeAnnotationSpec(name=core_type),  # 值为 core_type
                ],
            )

        elif container == ContainerType.ITERABLE:
            return TypeAnnotationSpec(
                name="Iterable", args=[TypeAnnotationSpec(name=core_type)]
            )

        elif container == ContainerType.CALLABLE:
            return TypeAnnotationSpec(
                name="Callable",
                args=[TypeAnnotationSpec(name="..."), TypeAnnotationSpec(name=core_type)],
            )

        else:
            raise ValueError(f"Unknown container type: {container}")

    def _make_optional(self, annotation: TypeAnnotationSpec) -> TypeAnnotationSpec:
        """将类型包装为可选类型 (Union[T, None])"""
        return TypeAnnotationSpec(
            name="Union", args=[annotation, TypeAnnotationSpec(name="None")]
        )

    def _extract_optional(
        self, annotation: TypeAnnotationSpec
    ) -> tuple[bool, TypeAnnotationSpec]:
        """如果是 Union[T, None] 或 Optional[T] 形式，返回 (True, T)"""
        # 情况 1: Union[T, None]
        if annotation.name == "Union":
            non_none_args = [arg for arg in annotation.args if arg.name != "None"]
            if len(non_none_args) == 1 and any(
                arg.name == "None" for arg in annotation.args
            ):
                return (True, non_none_args[0])

        # 情况 2: Optional[T]
        if annotation.name == "Optional" and len(annotation.args) == 1:
            return (True, annotation.args[0])

        return (False, annotation)

    def _extract_container_and_type(
        self, annotation: TypeAnnotationSpec
    ) -> tuple[ContainerType, str]:
        """从 TypeAnnotationSpec 提取容器类型和核心类型名"""

        # 情况 1: 无容器（无参数）
        if not annotation.args:
            return (ContainerType.NONE, annotation.name)

        # 情况 2: list[T] -> LIST, T
        if annotation.name == "list" and len(annotation.args) == 1:
            inner = annotation.args[0]
            # 检查嵌套容器：如果参数本身有参数，说明是嵌套容器
            if inner.args:
                raise ValueError(
                    f"Cannot convert complex type '{annotation.render()}' to AttributeSpec. "
                    f"Nested containers are not supported."
                )
            return (ContainerType.LIST, inner.name)

        # 情况 3: set[T] -> SET, T
        if annotation.name == "set" and len(annotation.args) == 1:
            inner = annotation.args[0]
            # 检查嵌套容器
            if inner.args:
                raise ValueError(
                    f"Cannot convert complex type '{annotation.render()}' to AttributeSpec. "
                    f"Nested containers are not supported."
                )
            return (ContainerType.SET, inner.name)

        # 情况 4: dict[str, T] -> MAP, T
        if annotation.name == "dict" and len(annotation.args) == 2:
            key_type, value_type = annotation.args[0].name, annotation.args[1].name
            if key_type == "str":
                # 检查嵌套容器：如果值类型有参数，说明是嵌套容器
                if annotation.args[1].args:
                    raise ValueError(
                        f"Cannot convert complex type '{annotation.render()}' to AttributeSpec. "
                        f"Nested containers are not supported."
                    )
                return (ContainerType.MAP, value_type)
            else:
                raise ValueError(
                    f"dict key type must be 'str' for AttributeSpec, got '{key_type}'"
                )

        # 情况 5: Iterable[T] -> ITERABLE, T
        # 宽容处理：Iterable, Sequence, Collection, Iterator 都视为 Iterable
        if annotation.name in ("Iterable", "Sequence", "Collection", "Iterator") and len(annotation.args) == 1:
            inner = annotation.args[0]
            if inner.args:
                raise ValueError(
                    f"Cannot convert complex type '{annotation.render()}' to AttributeSpec. "
                    f"Nested containers are not supported."
                )
            return (ContainerType.ITERABLE, inner.name)

        # 情况 6: Callable[[Args], Return] -> CALLABLE, Return
        # 宽容处理：忽略参数类型，仅保留返回值类型
        if annotation.name == "Callable":
            if len(annotation.args) == 2:
                # Callable[[Arg1, Arg2], ReturnType]
                # args[0] 是参数列表（可能是一个列表类型的 TypeAnnotationSpec），args[1] 是返回值
                return_type = annotation.args[1]
                # check nested container in return type
                if return_type.args:
                    raise ValueError(
                        f"Cannot convert complex type '{annotation.render()}' to AttributeSpec. "
                        f"Nested containers are not supported."
                    )
                return (ContainerType.CALLABLE, return_type.name)
            elif len(annotation.args) == 0:
                 # Callable (raw) -> treat as ANY
                 return (ContainerType.NONE, "Any")

        # 情况 5: 其他带参数的复杂类型（嵌套容器等）
        raise ValueError(
            f"Cannot convert complex type '{annotation.render()}' to AttributeSpec. "
            f"Nested containers are not supported."
        )
