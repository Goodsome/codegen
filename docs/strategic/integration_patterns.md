---
name: Codegen 全局集成与通信模式
description: 定义全局技术底座契约与集成规则
type: project
---

# 🔌 全局集成与通信模式 (Integration Patterns)

## 1. 上下文间通信契约

### 1.1 同步调用模式
所有上下文之间的同步调用**必须**通过依赖注入的应用服务接口实现，禁止直接调用其他上下文的领域层逻辑。

```python
# 正确模式：通过应用服务接口调用
from codegen.domain_definition.application.services import IBlueprintService

class OrchestrationService:
    def __init__(self, blueprint_service: IBlueprintService):
        self.blueprint_service = blueprint_service  # 依赖注入接口
    
    def handle_scaffold_command(self):
        blueprint = self.blueprint_service.load()  # 调用接口方法
```

### 1.2 数据传输契约
- 跨上下文传递的数据必须使用**不可变的数据传输对象 (DTO)**，禁止传递可变的领域实体对象。
- 所有 DTO 必须使用 Pydantic V2 定义，确保类型安全与序列化能力。
- 传输数据中不得包含任何上下文内部的实现细节。

## 2. 全局技术选型契约

| 技术领域 | 强制选型 | 备注 |
| --- | --- | --- |
| **包管理** | uv | 禁止手动修改 pyproject.toml，必须使用 `uv add/remove` |
| **依赖注入** | dependency-injector | 统一使用该框架实现组件装配 |
| **数据建模** | Pydantic V2 | 所有领域模型、DTO、配置均使用 Pydantic 定义 |
| **CLI 框架** | Typer | 所有命令行入口统一使用 Typer 实现 |
| **测试框架** | pytest | 统一使用 pytest 作为测试运行器 |
| **代码格式化** | black | 统一代码风格 |
| **代码检查** | ruff | 统一静态代码分析 |
| **类型检查** | basedpyright | 严格类型检查 |

## 3. 全局架构约束

### 3.1 分层架构约束
所有上下文必须严格遵循 DDD 四层架构：
```
┌─────────────────┐
│  Entrypoints    │  入口层：CLI/MCP 接口
├─────────────────┤
│  Application    │  应用层：用例编排、事务边界
├─────────────────┤
│  Domain         │  领域层：业务逻辑、实体、值对象、领域服务
├─────────────────┤
│  Infrastructure │  基础设施层：文件读写、外部服务调用
└─────────────────┘
```
- 依赖方向必须从外层向内层，禁止内层依赖外层
- 领域层绝对纯净，不得依赖任何外部技术框架

### 3.2 防腐层 (ACL) 约束
所有与外部系统（如 Python AST、文件系统、第三方工具）的交互必须通过防腐层隔离：
- 禁止在应用层/领域层直接调用 `ast` 模块 API
- 禁止在应用层/领域层直接操作文件系统
- 所有外部交互必须通过基础设施层的端口/适配器实现

## 4. MCP 工具契约
所有对外暴露的 MCP 工具必须遵循以下规则：
1. 工具名称必须遵循 `mcp__{context_name}__{tool_name}` 命名规范
2. 工具参数必须使用强类型定义，禁止使用泛型字符串参数
3. 工具实现必须放在对应上下文的 `entrypoints/mcp/` 目录下
4. 所有工具必须提供明确的错误返回与状态码
