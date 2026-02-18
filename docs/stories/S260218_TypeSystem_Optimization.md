# User Story: 类型系统优化 - AttributeSpec Container 支持

**Story ID**: S260218  
**创建时间**: 2026-02-18  
**状态**: Active  
**优先级**: High

---

## 1. 背景与问题陈述

### 1.1 当前状态

当前 `AttributeSpec` 中的 `type` 字段直接接受 Python 类型注释的字符串，例如：

```yaml
# 当前的写法（不通用）
attributes:
- name: items
  type: list[int]      # 直接写 Python 语法
- name: config
  type: dict[str, Any] # 依赖 Python 特定类型
- name: count
  type: int | None     # Python 3.10+ 联合类型语法
```

### 1.2 存在的问题

1. **语言耦合**: 直接嵌入 Python 类型语法，未来支持其他语言（TypeScript、Go、Rust）时无法复用
2. **复杂性不可控**: 支持任意层级的嵌套类型（`list[dict[str, list[int]]]`）增加了解析复杂度
3. **表达不一致**: 没有统一的方式表达"可选"（`Optional[T]` vs `T | None` vs `Union[T, None]`）

### 1.3 目标

设计一个**语言无关的通用类型系统**，能够：
- 清晰表达原语类型、容器类型和自定义类型
- 限制复杂度（最多一层 container 嵌套）
- 支持双向映射到具体语言的类型系统（特别是 Python）

---

## 2. 需求规格

### 2.1 codegen.yaml 模型变更（已完成）

已在 `codegen.yaml` 中更新 `AttributeSpec` 定义：

```yaml
value_objects:
- name: AttributeSpec
  description: Standard specification for a class attribute.
  attributes:
  - name: name
    type: SnakeString
  - name: description
    type: str
    optional: true
  - name: type              # 变更：限制为原语类型或自定义类型名
    type: str               # 值域: PrimitiveType 枚举 或 PascalString（自定义类型）
  - name: container         # 新增：容器类型
    type: ContainerType     # 值域: NONE, LIST, SET, MAP
    optional: true          # 默认: NONE
  - name: optional          # 是否可为 None
    type: bool
    optional: true          # 默认: false
  - name: default
    type: str | None
    optional: true
```

**约束**: 
- `type` 只能是通用原语类型（如 `string`, `integer`, `boolean`）或已定义的自定义类型名
- `container` 最多只能有一层（不嵌套）
- 当 `container=MAP` 时，键类型默认为 `string`（标准做法），值类型由 `type` 指定

### 2.2 类型映射表

| 通用类型表达 | Python 类型表达 | 说明 |
|-------------|----------------|------|
| `type: string` | `str` | 字符串 |
| `type: integer` | `int` | 整数 |
| `type: float` | `float` | 浮点数 |
| `type: boolean` | `bool` | 布尔值 |
| `type: datetime` | `datetime` | 日期时间 |
| `type: uuid` | `UUID` | UUID |
| `type: any` | `Any` | 任意类型 |
| `type: User` (自定义) | `User` | 引用其他 Value Object/Entity |
| `type: string, container: LIST` | `list[str]` | 字符串列表 |
| `type: integer, container: SET` | `set[int]` | 整数集合 |
| `type: User, container: MAP` | `dict[str, User]` | 用户字典（键为字符串） |
| `type: integer, optional: true` | `int \| None` | 可选整数 |
| `type: string, container: LIST, optional: true` | `list[str] \| None` | 可选字符串列表 |

---

## 3. 需要完成的工作

### 3.1 T2: 详细设计

**任务**: 设计 AttributeSpec 与 ParameterSpec 的转换策略

**产出**: `docs/design/type_system_conversion.md`

**内容要求**:
1. 通用类型系统 ↔ Python 类型系统的映射规则
2. `ContainerType + core_type + optional` → `TypeAnnotationSpec` 的转换算法
3. 反向解析：`TypeAnnotationSpec` → `ContainerType + core_type + optional` 的策略
4. 边界情况处理：
   - `dict[str, T]` 的反向解析（键必须是 str）
   - 嵌套容器类型的错误提示
   - 未知类型的处理

### 3.2 T3: 实现阶段

**Phase 1: 骨架生成**
- 更新 `codegen.yaml` 中的相关 Spec 定义
- 运行代码生成，生成新的 Python 类结构

**Phase 2: 测试先行**
- 编写 `AttributeMapper` 的单元测试
- 覆盖正常路径和异常路径
- 测试用例包含各种组合：原语类型、自定义类型、容器类型、可选类型

**Phase 3: 逻辑填充**
- 实现 `AttributeMapper.to_parameter_spec()` - 支持 container 字段
- 实现 `AttributeMapper.to_attribute()` - 从 TypeAnnotationSpec 提取 container
- 确保所有测试通过

---

## 4. 验收标准

### 4.1 设计文档验收
- [ ] 文档清晰定义了通用类型到 Python 类型的双向映射规则
- [ ] 包含完整的转换伪代码
- [ ] 识别并记录了所有边界情况和错误处理策略

### 4.2 功能验收
- [ ] `AttributeSpec` → `ParameterSpec` 转换正确处理 container：
  - `type="string", container=LIST` → `annotation="list[str]"`
  - `type="User", container=MAP` → `annotation="dict[str, User]"`
  - `type="integer", optional=true` → `annotation="int | None"`
- [ ] `ParameterSpec` → `AttributeSpec` 转换正确提取 container：
  - `annotation="list[int]"` → `type="integer", container=LIST`
  - `annotation="dict[str, User]"` → `type="User", container=MAP`
  - `annotation="str | None"` → `type="string", optional=true`
- [ ] 所有现有测试继续通过（向后兼容）

---

## 5. 技术注意事项

### 5.1 相关代码文件

| 文件 | 说明 |
|------|------|
| `src/codegen/domain_definition/domain/value_objects/attribute_spec.py` | AttributeSpec 模型 |
| `src/codegen/python_gen/domain/value_objects/parameter_spec.py` | ParameterSpec 模型 |
| `src/codegen/python_gen/domain/value_objects/type_annotation_spec.py` | TypeAnnotationSpec 模型 |
| `src/codegen/orchestration/domain/services/attribute_mapper.py` | 转换逻辑（需要修改） |
| `src/codegen/shared/domain/enums.py` | ContainerType 枚举 |

### 5.2 依赖关系

- `AttributeMapper` 依赖 `AttributeSpec` 和 `ParameterSpec`
- 修改后需要确保 `orchestration` 层的其他 Mapper（如 `ValueObjectMapper`, `EntityMapper`）正常工作
- 需要与 `AstTranslator` 的解析逻辑保持一致

---

## 6. 附录

### 6.1 变更前的示例

```yaml
# Before (Python 特定语法)
attributes:
- name: items
  type: list[str]
- name: mapping
  type: dict[str, int]
```

### 6.2 变更后的示例

```yaml
# After (通用类型表达)
attributes:
- name: items
  type: string
  container: LIST
- name: mapping
  type: integer
  container: MAP
```

### 6.3 PrimitiveType 枚举定义

```yaml
enums:
- name: PrimitiveType
  description: 通用原语类型，不依赖具体语言。
  members:
  - name: STRING
    value: string
  - name: INTEGER
    value: integer
  - name: FLOAT
    value: float
  - name: BOOLEAN
    value: boolean
  - name: DATETIME
    value: datetime
  - name: UUID
    value: uuid
  - name: ANY
    value: any
```

### 6.4 ContainerType 枚举定义

```yaml
enums:
- name: ContainerType
  members:
  - name: NONE
    value: none
  - name: LIST
    value: list
  - name: SET
    value: set
  - name: MAP
    value: map
```
