# 类型系统转换设计文档

**文档 ID**: D-TYPE-001  
**版本**: 1.0  
**创建日期**: 2026-02-18  
**状态**: Draft

---

## 1. 概述

### 1.1 设计目标

本文档定义通用类型系统（语言无关）与 Python 类型系统之间的双向映射规则，支持以下转换场景：

- **正向转换**: `AttributeSpec` → `ParameterSpec` (通用 → Python)
- **反向转换**: `ParameterSpec` → `AttributeSpec` (Python → 通用)

### 1.2 核心问题

| 问题 | 说明 |
|------|------|
| 类型名称映射 | 通用原语名称（`string`）→ Python 类型名（`str`） |
| 容器包装 | `container: LIST` → `list[T]` 语法 |
| 可选类型 | `optional: true` → `T \| None` 语法 |
| 复合场景 | 同时应用容器+可选：`list[str] \| None` |
| 反向解析 | 从 `TypeAnnotationSpec` 提取 `container` 和 `core_type` |

---

## 2. 类型映射规范

### 2.1 原语类型映射表

| 通用名称 (AttributeSpec.type) | Python 类型名 | 备注 |
|-------------------------------|---------------|------|
| `string` | `str` | |
| `integer` | `int` | |
| `float` | `float` | |
| `boolean` | `bool` | |
| `datetime` | `datetime` | 需导入 `datetime` |
| `uuid` | `UUID` | 需导入 `uuid.UUID` |
| `any` | `Any` | 需导入 `typing.Any` |
| `MyType` | `MyType` | 自定义类型名称透传 |

### 2.2 容器类型映射表

| ContainerType | Python 容器 | 参数化规则 |
|---------------|-------------|-----------|
| `NONE` | - | 直接使用原语类型 |
| `LIST` | `list[T]` | 单参数：`list[core_type]` |
| `SET` | `set[T]` | 单参数：`set[core_type]` |
| `MAP` | `dict[str, T]` | 双参数：键固定为 `str`，值为 `core_type` |

### 2.3 可选类型映射

| optional | Python 表达 |
|----------|------------|
| `false` | `T` |
| `true` | `T \| None` |

**注意**: 可选类型使用联合类型语法（Python 3.10+），在 `TypeAnnotationSpec` 中表现为 `Union[T, None]` 或直接 `T | None`。

---

## 3. 正向转换策略

### 3.1 转换流程

```
AttributeSpec
    ├── type: core_type (str)
    ├── container: ContainerType
    └── optional: bool
              ↓
         [转换步骤]
              ↓
TypeAnnotationSpec
    └── render() → Python 类型字符串
```

### 3.2 转换算法（伪代码）

```python
def to_parameter_spec(attribute: AttributeSpec) -> ParameterSpec:
    # 步骤 1: 映射核心类型名称
    python_type_name = PRIMITIVE_MAP.get(attribute.type, attribute.type)
    # PRIMITIVE_MAP = {"string": "str", "integer": "int", ...}
    
    # 步骤 2: 根据 container 包装类型
    annotation = _apply_container(python_type_name, attribute.container)
    # 返回 TypeAnnotationSpec
    
    # 步骤 3: 如果是可选类型，包装为 Union
    if attribute.optional:
        annotation = _make_optional(annotation)
    
    return ParameterSpec(
        name=attribute.name,
        annotation=annotation,
        optional=attribute.optional,
    )

def _apply_container(core_type: str, container: ContainerType) -> TypeAnnotationSpec:
    if container == ContainerType.NONE:
        return TypeAnnotationSpec(name=core_type)
    
    elif container == ContainerType.LIST:
        return TypeAnnotationSpec(
            name="list",
            args=[TypeAnnotationSpec(name=core_type)]
        )
    
    elif container == ContainerType.SET:
        return TypeAnnotationSpec(
            name="set",
            args=[TypeAnnotationSpec(name=core_type)]
        )
    
    elif container == ContainerType.MAP:
        return TypeAnnotationSpec(
            name="dict",
            args=[
                TypeAnnotationSpec(name="str"),  # 键固定为 str
                TypeAnnotationSpec(name=core_type)  # 值为 core_type
            ]
        )

def _make_optional(annotation: TypeAnnotationSpec) -> TypeAnnotationSpec:
    return TypeAnnotationSpec(
        name="Union",
        args=[annotation, TypeAnnotationSpec(name="None")]
    )
```

### 3.3 转换示例

| AttributeSpec | ParameterSpec.annotation.render() |
|---------------|----------------------------------|
| `type="string"`, `container=NONE` | `str` |
| `type="string"`, `container=LIST` | `list[str]` |
| `type="integer"`, `container=SET` | `set[int]` |
| `type="User"`, `container=MAP` | `dict[str, User]` |
| `type="string"`, `optional=true` | `Union[str, None]` → `str \| None` |
| `type="integer"`, `container=LIST`, `optional=true` | `Union[list[int], None]` → `list[int] \| None` |

---

## 4. 反向转换策略

### 4.1 转换流程

```
TypeAnnotationSpec
    ├── name: container_type (list/set/dict/其他)
    └── args: [参数列表]
              ↓
         [反向解析]
              ↓
AttributeSpec
    ├── type: core_type (通用名称或自定义类型)
    ├── container: ContainerType
    └── optional: bool
```

### 4.2 解析算法（伪代码）

```python
def to_attribute(parameter: ParameterSpec) -> AttributeSpec:
    annotation = parameter.annotation
    
    # 步骤 1: 检查可选类型（Union 且包含 None）
    is_optional, core_annotation = _extract_optional(annotation)
    
    # 步骤 2: 从 TypeAnnotationSpec 提取 container 和核心类型
    container, core_type_name = _extract_container_and_type(core_annotation)
    
    # 步骤 3: 将 Python 类型名反向映射为通用类型名
    generic_type = REVERSE_PRIMITIVE_MAP.get(core_type_name, core_type_name)
    # REVERSE_PRIMITIVE_MAP = {"str": "string", "int": "integer", ...}
    
    return AttributeSpec(
        name=parameter.name,
        type=generic_type,
        container=container,
        optional=is_optional,
    )

def _extract_optional(annotation: TypeAnnotationSpec) -> (bool, TypeAnnotationSpec):
    """如果是 Union[T, None] 形式，返回 (True, T)"""
    if annotation.name == "Union":
        non_none_args = [arg for arg in annotation.args if arg.name != "None"]
        if len(non_none_args) == 1 and any(arg.name == "None" for arg in annotation.args):
            return (True, non_none_args[0])
    return (False, annotation)

def _extract_container_and_type(annotation: TypeAnnotationSpec) -> (ContainerType, str):
    """从 TypeAnnotationSpec 提取容器类型和核心类型名"""
    
    # 情况 1: 无容器（无参数）
    if not annotation.args:
        return (ContainerType.NONE, annotation.name)
    
    # 情况 2: list[T] → LIST, T
    if annotation.name == "list" and len(annotation.args) == 1:
        return (ContainerType.LIST, annotation.args[0].name)
    
    # 情况 3: set[T] → SET, T
    if annotation.name == "set" and len(annotation.args) == 1:
        return (ContainerType.SET, annotation.args[0].name)
    
    # 情况 4: dict[str, T] → MAP, T
    if annotation.name == "dict" and len(annotation.args) == 2:
        key_type, value_type = annotation.args[0].name, annotation.args[1].name
        if key_type == "str":
            return (ContainerType.MAP, value_type)
        else:
            # MAP 的键不是 str，无法映射
            raise ConversionError(
                f"dict key type must be 'str' for AttributeSpec, got '{key_type}'"
            )
    
    # 情况 5: 其他带参数的复杂类型
    # 可选策略 A: 报错（严格模式）
    raise ConversionError(
        f"Cannot convert complex type '{annotation.render()}' to AttributeSpec. "
        f"Nested containers are not supported."
    )
    
    # 可选策略 B: 降级处理（宽松模式）
    # return (ContainerType.NONE, annotation.render())
```

### 4.3 反向转换示例

| TypeAnnotationSpec (Python) | AttributeSpec |
|-----------------------------|---------------|
| `str` | `type="string"`, `container=NONE` |
| `list[str]` | `type="string"`, `container=LIST` |
| `set[int]` | `type="integer"`, `container=SET` |
| `dict[str, User]` | `type="User"`, `container=MAP` |
| `str \| None` | `type="string"`, `optional=true` |
| `list[int] \| None` | `type="integer"`, `container=LIST`, `optional=true` |
| `dict[int, str]` | **ERROR** (键不是 str) |
| `list[list[int]]` | **ERROR** (嵌套容器不支持) |

---

## 5. 边界情况处理

### 5.1 正向转换边界

| 场景 | 处理策略 |
|------|----------|
| 未知的原语类型 | 透传原名称（假设为自定义类型） |
| container 与 core_type 不兼容 | 允许（如 `list[datetime]` 是合法的） |
| 多层嵌套 (代码逻辑缺陷) | 当前设计已限制，需 Schema 层校验 |

### 5.2 反向转换边界

| 场景 | 处理策略 | 示例 |
|------|----------|------|
| `dict[int, str]` (非 str 键) | **报错** | 键必须是 `str` |
| `list[list[int]]` (嵌套容器) | **报错** | 不支持嵌套 |
| `Optional[T]` vs `T \| None` | **统一处理** | 两者都识别为 `optional=true` |
| `tuple[T, ...]` | **报错** | 不支持的容器类型 |
| 复杂联合类型 | **报错** | `int \| str` 无法映射 |

### 5.3 类型映射表扩展

**Python → 通用反向映射表 (REVERSE_PRIMITIVE_MAP)**:

```python
{
    # 基本类型
    "str": "string",
    "int": "integer", 
    "float": "float",
    "bool": "boolean",
    "None": "none",
    
    # 需要导入的类型
    "datetime": "datetime",
    "UUID": "uuid",
    "Any": "any",
}
```

**处理未映射类型**:
- 如果类型名不在映射表中，视为**自定义类型名**，透传到 `AttributeSpec.type`
- 这允许引用用户自定义的 Value Objects 和 Entities

---

## 6. 集成策略

### 6.1 AttributeMapper 修改点

```python
class AttributeMapper:
    # 正向转换
    def to_parameter_spec(self, attribute: AttributeSpec, ...) -> ParameterSpec:
        # 修改前: 直接 parse_type_str(attribute.type)
        # 修改后: 按上述算法构建 TypeAnnotationSpec
        ...
    
    # 反向转换  
    def to_attribute(self, parameter: ParameterSpec) -> AttributeSpec:
        # 修改前: type=parameter.annotation.render()
        # 修改后: 按上述算法提取 container 和 core_type
        ...
```

### 6.2 依赖变更

| 组件 | 当前依赖 | 新增依赖 |
|------|----------|----------|
| `AttributeMapper` | `parse_type_str()` | 需要实现 `_apply_container()` 等转换函数 |
| | | 需要双向映射字典 |

### 6.3 辅助工具函数建议

建议新增工具类或模块：

```python
class TypeSystemConverter:
    """通用类型系统与 Python 类型系统的转换器"""
    
    PRIMITIVE_MAP: dict[str, str]  # 通用 → Python
    REVERSE_MAP: dict[str, str]    # Python → 通用
    
    @classmethod
    def to_python_annotation(cls, attr: AttributeSpec) -> TypeAnnotationSpec:
        ...
    
    @classmethod  
    def from_python_annotation(cls, annotation: TypeAnnotationSpec) -> tuple[str, ContainerType, bool]:
        """返回: (core_type, container, is_optional)"""
        ...
```

---

## 7. 测试策略

### 7.1 测试覆盖矩阵

| 类型组合 | 正向 | 反向 |
|----------|------|------|
| 原语类型 (`string`, `integer`...) | ✅ | ✅ |
| 自定义类型 | ✅ | ✅ |
| LIST 容器 | ✅ | ✅ |
| SET 容器 | ✅ | ✅ |
| MAP 容器 | ✅ | ✅ |
| 可选类型 | ✅ | ✅ |
| 容器+可选组合 | ✅ | ✅ |
| 嵌套容器（错误场景） | ✅ | N/A |
| 非 str 键 MAP（错误场景） | N/A | ✅ |

### 7.2 关键测试用例

```python
# 正向转换测试
def test_list_of_strings():
    attr = AttributeSpec(type="string", container=ContainerType.LIST)
    param = mapper.to_parameter_spec(attr)
    assert param.annotation.render() == "list[str]"

def test_optional_map():
    attr = AttributeSpec(type="User", container=ContainerType.MAP, optional=True)
    param = mapper.to_parameter_spec(attr)
    assert param.annotation.render() == "dict[str, User] | None"

# 反向转换测试
def test_list_annotation():
    spec = TypeAnnotationSpec(name="list", args=[TypeAnnotationSpec(name="int")])
    param = ParameterSpec(name="items", annotation=spec)
    attr = mapper.to_attribute(param)
    assert attr.type == "integer"
    assert attr.container == ContainerType.LIST
    assert attr.optional == False

def test_dict_with_non_str_key():
    spec = TypeAnnotationSpec(name="dict", args=[
        TypeAnnotationSpec(name="int"),  # 错误的键类型
        TypeAnnotationSpec(name="str")
    ])
    param = ParameterSpec(name="mapping", annotation=spec)
    with pytest.raises(ConversionError):
        mapper.to_attribute(param)
```

---

## 8. 附录

### 8.1 参考文件

- `src/codegen/shared/domain/enums.py` - ContainerType, PrimitiveType 定义
- `src/codegen/domain_definition/domain/value_objects/attribute_spec.py` - AttributeSpec 模型
- `src/codegen/python_gen/domain/value_objects/parameter_spec.py` - ParameterSpec 模型
- `src/codegen/python_gen/domain/value_objects/type_annotation_spec.py` - TypeAnnotationSpec 模型
- `src/codegen/orchestration/domain/services/attribute_mapper.py` - 需要修改的转换器

### 8.2 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-02-18 | 初始版本，定义双向转换规则 |

---

## 9. 待决策事项

| 事项 | 选项 | 推荐 |
|------|------|------|
| 反向遇到嵌套容器 | A. 报错  B. 降级为字符串 | **A**（严格模式，清晰） |
| `dict[str, Any]` | 如何表达 Any 值类型？ | `type="any", container=MAP` |
| 时区感知 datetime | 需要额外字段吗？ | 暂时不需要，统一为 `datetime` |
