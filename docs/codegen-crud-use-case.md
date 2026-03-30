# Codegen CRUD Use Case Implementation Guide

本指南描述如何在 Codegen 项目中实现 CRUD 用例。

## 流程概览

1. **更新 `codegen.yaml`** - 在目标上下文的 `application.use_cases` 下添加用例定义
2. **运行 `codegen build`** - 从 blueprint 生成 Python 代码
3. **实现 `execute` 方法** - 编写业务逻辑

---

## Step 1: 更新 codegen.yaml

### 用例定义模板

```yaml
- name: Add<EntityName>          # Add 前缀表示创建操作
  kind: command                  # 或 query
  inputs:
  - type: string
    name: context_name           # 定位上下文（若有）
  - type: string
    name: name
  - type: string
    name: description
  outputs:
  - type: boolean
    name: success
  dependencies:
  - type: BlueprintStorage
    name: storage
```

### 用例命名规范

| 操作 | 命名示例 | 说明 |
|------|----------|------|
| Create | `AddAggregate` | 添加新实体 |
| Read | `GetAggregate` / `LoadBlueprint` | 获取单个或所有 |
| Update | `UpdateAggregate` | 更新已有实体 |
| Delete | `RemoveAggregate` | 删除实体 |

### 查找用例添加位置

```bash
# 查找所有 application.use_cases 位置
grep -n "application:" codegen.yaml | head -10

# 查找特定上下文（如 DomainDefinition）
grep -n "^- name:" codegen.yaml
```

### 用例存放位置

| 上下文 | 文件路径 |
|--------|----------|
| `DomainDefinition` | `src/codegen/domain_definition/application/use_cases/` |
| `PythonGen` | `src/codegen/python_gen/application/use_cases/` |
| `Orchestration` | `src/codegen/orchestration/application/use_cases/` |

---

## Step 2: 运行 codegen build

```bash
codegen build
```

这会在 `src/codegen/<context>/application/use_cases/` 下生成用例文件。

### 生成的代码结构

```python
from dataclasses import dataclass
from pydantic import BaseModel
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class AddAggregateCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddAggregateResult(BaseModel):
    success: bool


@dataclass
class AddAggregate:
    storage: BlueprintStorage

    def execute(self, cmd: AddAggregateCommand) -> AddAggregateResult: ...
```

---

## Step 3: 实现 execute 方法

### 参考现有实现

```bash
# 查看类似用例实现
cat src/codegen/domain_definition/application/use_cases/upsert_context.py
```

### 实现模式

```python
def execute(self, cmd: AddAggregateCommand) -> AddAggregateResult:
    # 1. 加载 blueprint
    blueprint = self.storage.load()
    if blueprint is None:
        raise ValueError("Blueprint not loaded")

    # 2. 获取上下文
    context = blueprint.get_context(cmd.context_name)

    # 3. 创建实体
    aggregate = AggregateSpec(
        name=PascalString(cmd.name),
        description=cmd.description,
    )

    # 4. 添加到领域模型
    context.domain.add_aggregate(aggregate)

    # 5. 保存
    self.storage.save(blueprint)

    return AddAggregateResult(success=True)
```

### 关键导入

```python
from codegen.domain_definition.domain.entities.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString
```

### 错误处理

- **不要使用 try-except** - 错误直接暴露，让调用者处理
- 常见异常：`ValueError`（实体不存在、已存在）

### 领域模型查找

```bash
# 查找实体的 CRUD 方法
grep -n "def add_\|def update_\|def remove_\|def get_" src/codegen/domain_definition/domain/entities/domain_spec.py
```

---

## 完整示例

参见：`src/codegen/domain_definition/application/use_cases/add_aggregate.py`

---

## 验证

```bash
# Lint
uv run ruff check src/codegen/domain_definition/application/use_cases/add_aggregate.py

# 测试
uv run pytest tests/ -x -q
```

---

## 常见模式

### 添加到列表（如 aggregates、entities）

```python
context.domain.add_aggregate(aggregate)  # DomainSpec.add_aggregate()
```

### 更新

```python
context.domain.update_aggregate(aggregate)
```

### 移除

```python
context.domain.remove_aggregate(name)
```

### 直接设置值

```python
# 使用 BlueprintPathOperations
operations = BlueprintPathOperations(resolver=BlueprintPathResolver())
blueprint = operations.set_value(blueprint, "contexts.sales", new_context, append=True)
```
