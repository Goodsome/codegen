# Issue Tracking

> Last updated: 2026-03-26

本文档用于跟踪 Codegen 项目中的问题、缺陷和改进建议。

## 如何添加新 Issue

1. 新 Issue 使用 uuid 作为编号
2. 在 Issue 列简述问题
3. 在 Notes 列填相关描述
4. 填写详细信息，比如 BUG 复现场景。

## 如何清理已处理的 Issue

当某个 Issue 被修复后，从表格和下方详细信息中同步删除该条目。

---

## Issue 详情模板

复制以下模板创建新 Issue：

```markdown
## {uuid} - {Issue 标题}

### 描述 (Description)

{详细描述问题或需求，包括相关代码片段}

### 期望行为 (Expected Behavior)

{描述期望的正确行为}

### 建议的实现方案 (Proposed Solution)

{描述建议的解决方案，可以包含代码示例}

### 任务清单 (Tasks)

- [ ] {任务1}
- [ ] {任务2}
- [ ] {任务3}

### 创建时间
{YYYY-MM-DD}

---
```

---

| # | Issue | Severity | Status | Notes |
|-------|-------|----------|--------|-------|
| `3f8a1b2c-4d5e-4f6a-b7c8-d9e0f1a2b3c4` | 扩展 `AssignmentSpec` 以支持 Subscript 语法解析 | Feature | Open | 支持 `Provide["..."]` 等下标语法的结构化解析 |
| `4e9b2c3d-5f6a-4d7e-8a9b-0c1d2e3f4a5b6` | AttributeSpec.default 字面量类型问题 | Bug | Open | `default: False` 实际表现为字符串 `"False"` 而非布尔值 |

---

## 3f8a1b2c-4d5e-4f6a-b7c8-d9e0f1a2b3c4 - 扩展 `AssignmentSpec` 以支持 Subscript 语法解析

### 描述 (Description)

当前 `AssignmentSpec` 模型无法在结构层面精确描述类似依赖注入中的下标语法，例如：

```python
use_case: GenerateProject = Provide["orchestration_container.generate_project_use_case"]
```

目前对于 `Provide["..."]` 这种 AST 中的 `Subscript` 节点，模型只能退化使用 `AssignmentFlavor.CODE` 作为纯文本进行存储。这导致我们丧失对其进行结构化解析的能力，特别是 `get_required_types()` 无法自动识别并提取出 `Provide` 这个依赖符号。

### 期望行为 (Expected Behavior)

引入对 `Subscript` 语法的支持，使得 `AssignmentSpec` 能够将 `obj[key]` 拆解为被索引的对象 (value) 和索引内容 (slice)，并能正确参与依赖类型的收集。

### 建议的实现方案 (Proposed Solution)

1. **新增值对象 `SubscriptSpec`**：包含 `value` (对应 `AssignmentSpec`) 和 `slice` (对应 `AssignmentSpec`) 两个字段。
2. **扩展枚举**：在 `AssignmentFlavor` 中增加 `SUBSCRIPT` 类型。
3. **扩展 `AssignmentSpec`**：
   - 增加 `subscript: SubscriptSpec | None = Field(default=None)` 字段。
   - 增加 `@classmethod def from_subscript(...)` 工厂方法。
4. **完善依赖解析**：更新 `AssignmentSpec.get_required_types()` 方法，使其能递归收集 `subscript.value` 和 `subscript.slice` 中的类型。

### 任务清单 (Tasks)

- [ ] 定义 `SubscriptSpec` 类
- [ ] 更新 `AssignmentFlavor` 和 `AssignmentSpec` 模型
- [ ] 更新 `get_required_types` 逻辑
- [ ] 添加对应的单元测试，确保 `Provide["..."]` 能被正确解析，并且能从中提取到 `Provide`

### 创建时间
2026-03-26

---

## 4e9b2c3d-5f6a-4d7e-8a9b-0c1d2e3f4a5b6 - AttributeSpec.default 字面量类型问题

### 描述 (Description)

`AttributeSpec.default` 字段类型由 `str` 改为 `Any` 后，实际表现仍与预期不符：

1. **codegen.yaml 字段值问题**：`default: False` 被存储为字符串 `"False"` 而非字面量 `False`
2. **生成代码类型问题**：生成的代码中 `default="False"` 是字符串，而非布尔值 `False`

**问题根因**：`AttributeSpec.to_variable_spec()` 方法在处理 `default` 值时：

```python
if self.default is not None:
    if self.default == "":
        assignment = AssignmentSpec.from_literal("")
    else:
        assignment = AssignmentSpec.from_code(self.default)  # 错误：False 被当作 "False" 处理
```

当 `self.default` 实际值为 `False`（布尔值）时，代码进入 `from_code("False")` 分支，将其作为代码字符串处理，而非字面量。

### 期望行为 (Expected Behavior)

1. `codegen.yaml` 中的 `default` 字段应存储实际字面量值（如 `False`、`True`、`None`、数字等）
2. 生成代码应输出真实的字面量（如 `default=False`），而非字符串（如 `default="False"`）

### 建议的修复方案 (Proposed Solution)

修改 `AttributeSpec.to_variable_spec()` 中的逻辑，区分字面量值和代码字符串：

```python
if self.default is not None:
    if isinstance(self.default, str):
        if self.default == "":
            assignment = AssignmentSpec.from_literal("")
        else:
            assignment = AssignmentSpec.from_code(self.default)
    else:
        # 处理实际字面量（bool, int, float, None 等）
        assignment = AssignmentSpec.from_literal(self.default)
```

### 任务清单 (Tasks)

- [ ] 修复 `AttributeSpec.to_variable_spec()` 中的类型判断逻辑
- [ ] 验证 `False`、`True`、`None` 等字面量在 codegen.yaml 和生成代码中的正确性
- [ ] 添加单元测试覆盖字面量 default 场景

### 创建时间
2026-03-26

---
