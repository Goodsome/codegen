# Issue Tracking

> Last updated: 2026-04-01

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
| 7a3f8e2c | codegen reverse: Field with default_factory 生成 optional: true 而非 default | Medium | Open | reverse 生成的 yaml 中 default_factory 字段被生成为 optional: true |
| 9d4f1b7e | DomainSpec.behaviors 的 classmethod 方法缺少 @classmethod 装饰器 | High | Open | from_package_spec 方法缺少 @classmethod |

---

## 7a3f8e2c - codegen reverse: Field with default_factory 生成 optional: true 而非 default

### 描述 (Description)

当使用 `codegen reverse` 逆向解析包含 `default_factory` 的 Pydantic model 时，生成的 codegen.yaml 格式不正确。

原始代码：
```python
class DomainSpec(Entity):
    """Specification of a domain to be generated."""

    aggregates: list[AggregateSpec] = Field(default_factory=list)
```

实际生成的 codegen.yaml：
```yaml
- name: DomainSpec
  description: Specification of a domain to be generated.
  attributes:
  - type: AggregateSpec
    container: list
    optional: true
    name: aggregates
```

### 期望行为 (Expected Behavior)

应生成 `default: []` 而非 `optional: true`：
```yaml
- name: DomainSpec
  description: Specification of a domain to be generated.
  attributes:
  - type: AggregateSpec
    container: list
    name: aggregates
    default: []
```

### 任务清单 (Tasks)

- [ ] 定位 reverse 生成 attributes 的代码位置
- [ ] 添加判断逻辑：default_factory → default, required=False → optional: true
- [ ] 验证修复后的输出

### 创建时间
2026-04-01

---

## 9d4f1b7e - DomainSpec.behaviors 的 classmethod 方法缺少 @classmethod 装饰器

### 描述 (Description)

在 `codegen reverse` 生成的 `DomainSpec.behaviors` 中，带有 `cls` 字段作为第一个参数的类方法缺少 `@classmethod` 装饰器。

原始代码（DomainSpec.behaviors）：
```python
- name: from_package_spec
  description: 将 PackageSpec 逆向解析为 DomainSpec
  inputs:
  - type: Self
    container: type
    name: cls
  - type: PackageSpec
    name: package_spec
  output:
    type: DomainSpec
```

实际生成的代码缺少 `@classmethod` 装饰器。

### 期望行为 (Expected Behavior)

生成的代码应包含 `@classmethod` 装饰器：
```python
@classmethod
def from_package_spec(cls, package_spec: PackageSpec) -> DomainSpec:
    """将 PackageSpec 逆向解析为 DomainSpec"""
    ...
```

### 任务清单 (Tasks)

- [ ] 定位 behaviors 代码生成逻辑
- [ ] 添加 classmethod 检测和装饰器生成
- [ ] 验证修复后的输出

### 创建时间
2026-04-01

---
