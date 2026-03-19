# Feature

* 增加tree get set的能力，不要再直接查询 codegen.yaml
  * set需要校验，并返回具体信息，而不是啥都往里面写
  * reverse codegen.yaml 改动太大了。主要问题是codegen.yaml 没有规定的顺序
* build 问题
  * enum
  * naming问题，比如：SOP
* 支持interfaces
* 支持bootstrap
  * 上下文中的container
* 支持entrypoints
* 代码清理工具

## 专属的 Bootstrap 目录（适合大型项目）
如果你的初始化逻辑很复杂（比如除了 DI 容器，还有日志配置、遥测 OpenTelemetry 设置、数据库连接池初始化等），可以单独开一个目录。
src/codegen
├── bootstrap/           <-- 【新增】启动引导层
│   ├── __init__.py
│   ├── container.py     <-- 定义 DI 容器
│   ├── config.py        <-- 加载配置
│   └── logging.py       <-- 配置日志
├── entrypoints/
├── domain_definition/
└── ...

## RENAME

什么时候你才真正需要记录“元数据”？
只有在一个极其特殊的痛点下，纯靠目录约定会失效：重命名（Renaming）追踪。
如果开发者在代码里把 CreateOrderUseCase 改成了 PlaceOrderUseCase，纯按名称匹配的逆向解析器可能会认为：旧的被删除了，同时新建了一个。它无法把修改前的 YAML 节点和修改后的代码关联起来。

即使未来要解决这个问题，更好的做法也不是在业务代码里写元数据，而是：

外置状态文件：类似 .codegen.lock 或 .codegen.state.json，在项目根目录维护一个文件 ID 到当前 AST 签名的映射字典（对业务代码零侵入）。

基于特征的启发式匹配：比较 AST 树的相似度（比如类里的方法没变，只是类名变了，判定为 Rename）。


---

  【工具反馈】

  ⚠️ 遇到的问题

  1. 数组追加语法不支持：contexts[-] 和 contexts[2]（索引越界时）均失败，必须使用 append: true 参数。
  2. JSON 字符串误写入：添加 IssueEventPublisher 端口时，工具将 JSON 对象作为原始字符串写入 YAML，导致格式损坏。需手动修复。
  3. default 字段类型限制：ConfigFieldSpec 的 default 字段只接受字符串类型，整数值需转为字符串（如 '10'）。
  4. output type: None' 也生成错误的代码。未做校验。

  💡 工具优化建议

  ┌────────────────────┬─────────────────────────────────────────────────┬──────────────────────────────────────┐
  │       建议项       │                    期望功能                     │                 价值                 │
  ├────────────────────┼─────────────────────────────────────────────────┼──────────────────────────────────────┤
  │ 支持 [-] 追加语法  │ 无需每次指定 append: true                       │ 减少认知负担，与常见 YAML 操作一致   │
  ├────────────────────┼─────────────────────────────────────────────────┼──────────────────────────────────────┤
  │ 批量写入接口       │ mcp__codegen__set_bulk 支持一次写入多个同级组件 │ 减少网络往返，提升大量组件写入效率   │
  ├────────────────────┼─────────────────────────────────────────────────┼──────────────────────────────────────┤
  │ JSON 对象正确解析  │ 确保 set 操作正确解析嵌套对象而非写入字符串     │ 避免格式损坏                         │
  ├────────────────────┼─────────────────────────────────────────────────┼──────────────────────────────────────┤
  │ 验证错误时仍可操作 │ 当存在验证错误时，允许删除/修复损坏元素         │ 当前因验证错误阻断，无法使用工具修复 │
  └────────────────────┴─────────────────────────────────────────────────┴──────────────────────────────────────┘

---

## 代码生成问题（2026-03-19）

### P1: CLI 命令名含空格时，`__init__.py` 导入语句未转换为合法标识符

**问题描述**：
当 CLI 命令名包含空格（如 `issue create`）时，文件名正确转换为 `issue_create.py`，但 `__init__.py` 中的导入语句仍使用原始名称。

**错误示例**：
```python
# 错误：模块名和导入名包含空格
from xxx.issue create import issue create

# 正确应为
from xxx.issue_create import issue_create
```

**影响范围**：`interfaces/cli/__init__.py`

**建议修复**：
```python
def sanitize_identifier(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_")
```

---

### P2: 类方法返回自身类型时，未添加 `from __future__ import annotations`

**问题描述**：
生成的值对象、实体、聚合根中，方法返回类型为类自身时（如 `def create(...) -> IssueId`），会导致 `NameError: name 'IssueId' is not defined`。

**错误示例**：
```python
class IssueId(ValueObject):
    value: UUID

    def create(self) -> IssueId: ...  # NameError!
```

**正确做法**：
```python
from __future__ import annotations  # 必须添加

class IssueId(ValueObject):
    value: UUID

    def create(self) -> IssueId: ...  # OK
```

**影响范围**：所有值对象、实体、聚合根

**建议修复**：所有生成的类文件默认添加 `from __future__ import annotations`

---

### P3: 外部类型未自动导入

**问题描述**：
蓝图中定义的外部类型（如 `Session`, `Connection`, `DomainEvent`）在生成代码时未自动导入，导致 `NameError`。

**受影响文件**：
- `infrastructure/repositories/*.py` - 缺少 `Session` 导入
- `infrastructure/adapters/*.py` - 缺少 `Connection` 等导入
- `domain/ports/*.py` - 缺少 `DomainEvent` 等类型导入

**建议修复方案**：
1. 支持在蓝图中声明外部类型导入：
   ```yaml
   implementations:
   - name: SqlAlchemyIssueRepository
     implements: IssueRepository
     technology: sql
     external_imports:
     - from: sqlalchemy.orm
       import: Session
   ```
2. 或自动检测未定义类型并生成占位导入/类型别名

---

### P4: `--node` 参数行为异常

**问题描述**：
使用 `--node` 参数更新单个组件时，会替换整个数组而非匹配元素，导致其他元素丢失。

**示例**：
```yaml
# 原始
use_cases:
- name: CreateIssue
- name: UpdateIssueStatus
- name: ListIssues

# 执行 mcp__codegen__set --node CreateIssue 后
use_cases:
- name: CreateIssue  # 其他两个丢失！
```

**建议修复**：`--node` 应定位匹配元素并更新，而非替换整个数组。

---

### 问题影响矩阵

| 问题 | 严重程度 | 是否阻断 | 临时解决方案 |
|------|---------|---------|-------------|
| P1: CLI 标识符转换 | 高 | 是 | 手动修复 `__init__.py` |
| P2: 前向引用缺失 | 高 | 是 | 手动添加 `__future__` 导入 |
| P3: 外部类型未导入 | 高 | 是 | 手动添加占位导入 |
| P4: `--node` 行为异常 | 高 | 是 | 避免使用 `--node` |
  
