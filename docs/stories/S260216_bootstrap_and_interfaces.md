这是一版经过修订的用户故事文档。

**主要的修订点**在于 **1.1 Container 按上下文层级拆分** 部分。根据我们在上一轮对话中的讨论，为了保证上下文的高内聚（High Cohesion）和接口层（Interfaces）的便利性，**各上下文的容器应位于各自的上下文目录下**，而不是集中在 `bootstrap` 目录下。

以下是修订后的完整文档：

---

# User Story: Bootstrap 标准化与 Interfaces 层支持 (Revised)

## 背景

Codegen 项目的愿景是创建符合 DDD 的标准代码骨架生成器。当前项目在 **bootstrap（启动引导）** 和 **interfaces（接口适配层）** 两个方面存在缺失，不能作为 DDD 标准骨架的参考实现。

### 现状分析

#### Bootstrap 现状

* `src/codegen/bootstrap.py` 中存在一个扁平的 `Container` 类，全部依赖混杂。
* 所有上下文（DomainDefinition, Orchestration, PythonGen, Shared）的依赖全部挤在同一个容器中。
* 配置（config）以原始 `dict` 形式分散定义，缺乏类型安全和环境隔离。
* `codegen.yaml` 中 `BootstrapSpec` 定义缺失，无法描述容器和配置结构。

#### Interfaces 现状

* `src/codegen/entrypoints/` 目录下的 CLI 和 MCP 实现游离于架构之外。
* `codegen.yaml` 中的 `BoundedContext` 缺乏 `interfaces` 层定义，无法通过 DSL 生成接口代码。

---

## 需求定义

### 1. Bootstrap 标准化

#### 1.1 Container 按上下文层级拆分与归位

**标准定义**：Bootstrap 层的 DI 容器需要按 Bounded Context 进行拆分。**Root Container** 位于 `bootstrap` 层，负责集成；**Context Container** 位于各自的上下文目录内，负责上下文内部的组装。

**目标目录结构：**

```
src/project/
├── bootstrap/
│   ├── __init__.py
│   ├── config.py           # 全局配置（pydantic_settings）
│   └── container.py        # Root Container（组合各上下文容器）
├── shared/
│   └── container.py        # Shared Container (日志、基础工具等)
├── context_a/
│   ├── container.py        # ContextAContainer (定义在上下文内部)
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── interfaces/         # ContextA 的接口层，可直接引用同级 container
└── context_b/
    ├── container.py        # ContextBContainer
    └── ...

```

**设计要点：**

* **Root Container (`bootstrap/container.py`)**：作为 Composition Root，负责加载全局配置，实例化 Shared Container，并装配所有 Context Container。
* **Context Container (`context_a/container.py`)**：定义该上下文内部 UseCase、Service、Repository 的依赖关系。它仅暴露 `bootstrap` 需要的入口，或供内部 `interfaces` 使用。
* **依赖传递**：Root Container 将 Shared Container 或 Global Config 注入到各 Context Container 中。

#### 1.2 Config 使用 pydantic_settings 实现

**标准定义**：配置管理使用 `pydantic_settings` 的 `BaseSettings` 实现。

**设计要点：**

* **Global Config**：在 `bootstrap` 中定义全局通用配置。
* **Context Config**：支持在 `BoundedContext` 中定义该上下文独有的配置类（可选）。
* **注入方式**：`BaseSettings` 实例作为 `Configuration` provider 注入到 Container 中。

### 2. Interfaces 层支持

#### 2.1 Interfaces 层作为 DDD 分层架构的标准组成部分

**标准定义**：`interfaces` 是 DDD 四层架构的最外层，负责将 Application Layer 的 Use Case 暴露给外部世界（用户或 AI）。

**BoundedContext 扩展（DSL）：**

```yaml
# codegen.yaml
- name: SomeContext
  domain: ...
  application: ...
  infrastructure: ...
  bootstrap: 
    config: ...           # 新增：上下文级配置定义
    container: ...        # 新增：上下文级容器定义
  interfaces:           # 新增：接口层定义
    mcp:                # 定义 MCP Tools
       tools: ...
    cli:                # 定义 CLI Commands
       commands: ...
    http:               # (Future) 定义 HTTP Endpoints
       ...

```

#### 2.2 支持的协议类型与实现细节

1. **MCP (Model Context Protocol)**
* **框架**：`fastmcp`
* **机制**：`codegen` 需生成一个 `mcp_server.py`（位于 `interfaces/mcp/`），该文件实例化 MCP Server，并从 `ContextContainer` 中获取 UseCase，将其包装为 MCP Tool。
* **DSL 映射**：`McpToolSpec` -> `mcp.tool()` 装饰器函数。


2. **CLI (Command Line Interface)**
* **框架**：`typer`
* **机制**：`codegen` 需生成 `cli.py`（位于 `interfaces/cli/`），定义 `typer.Typer` 应用。命令函数从 `ContextContainer` 获取 UseCase 执行逻辑。
* **DSL 映射**：`CliCommandSpec` -> `typer.command()` 函数。



#### 2.3 Interfaces 层与 Bootstrap 的关系

* **Context 内部接口**：`src/context_a/interfaces/cli.py` 直接导入同级的 `src/context_a/container.py` 来获取依赖，保持上下文闭环。
* **全局入口**：`src/entrypoints/`（如主 CLI 入口）负责导入 `src/bootstrap/container.py`，初始化 Root Container，并将各 Context 的 Interface 注册到主程序中。

---

## 验收标准

### Bootstrap & Config

* [ ] **DSL 更新**: `codegen.yaml` 支持 `BootstrapSpec` (含 RootContainer, GlobalConfig) 和 `BoundedContext` (含 Config, Container) 的定义。
* [ ] **代码生成**: 生成的目录结构符合上述 1.1 的定义，Container 分散在各 Context 目录中。
* [ ] **配置实现**: 生成的代码使用 `pydantic_settings`，支持 `.env` 读取。
* [ ] **依赖注入**: 生成的 Root Container 能正确串联 Shared Container 和 Context Containers。

### Interfaces

* [ ] **DSL 更新**: `BoundedContext` 支持 `interfaces` 节点，包含 `mcp` 和 `cli` 定义。
* [ ] **MCP 生成**: 能根据 Blueprint 生成 `mcp_server.py`，且能正确调用 UseCase。
* [ ] **CLI 生成**: 能根据 Blueprint 生成 `cli.py`，参数正确映射到 UseCase Input DTO。
* [ ] **依赖获取**: 生成的接口代码通过 Container (`providers.Factory`) 获取 UseCase 实例，不直接实例化类。

---

## 约束与技术选型

* **DI 框架**: `dependency-injector` (DeclarativeContainer 模式)
* **配置管理**: `pydantic-settings`
* **CLI 框架**: `typer`
* **MCP 框架**: `fastmcp` (基于 mcp-python-sdk)
* **Python 版本**: 保持一致