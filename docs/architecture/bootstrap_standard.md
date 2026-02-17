# ADR: Bootstrap 标准化设计 (Revised v2)

## Status

**Proposed** | 2026-02-17

## Context

Codegen 项目是一个符合 DDD 的标准代码骨架生成器。当前 Bootstrap 层存在结构混乱、配置分散且缺乏类型安全的问题，无法支撑复杂的应用启动需求。

### 现状问题

1. **BootstrapSpec 缺失**：当前 `codegen.yaml` 无法描述容器层级结构和配置定义。
2. **Container 扁平化**：所有上下文的依赖混杂在同一个 Container 类中，违反边界隔离原则。
3. **Config 原始化**：配置以字典形式分散定义，缺乏统一管理和类型检查。

### 关联 User Story

- Ref: `docs/stories/S260216_bootstrap_and_interfaces.md`

---

## Decision

### 1. BootstrapSpec 元模型扩展

#### 1.1 设计原则

BootstrapSpec 负责描述应用的**引导层结构**。

- **声明式**：描述“有什么配置”、“有什么容器定制”。
- **层级化**：支持 Root Container 和 Context Container 的树状结构。

#### 1.2 BoundedContext 扩展

在 `BoundedContext` 中新增 `config` 和 `container` 节点，允许上下文定义自己的配置结构和依赖注入规则。

### 2. Config 聚合与管理策略

#### 2.1 策略定义：分散定义，集中加载

为了兼顾“高内聚”与“统一运维”，我们采用以下配置策略：

1.  **定义分散 (High Cohesion)**：每个 Bounded Context 在其内部定义自己的配置类（如 `ContextASettings`），描述该上下文所需的字段。
2.  **加载集中 (Centralized Loading)**：`bootstrap/config.py` 中的 `AppSettings` 负责聚合所有 Context 的配置类。
3.  **统一入口 (Single Source)**：所有配置值统一从根目录的 `.env` 文件（或环境变量）读取。
4.  **依赖注入**：Root Container 实例化 `AppSettings`，并将对应的配置分片注入到各 Context Container。

#### 2.2 元模型 Schema (ConfigSpec)

合并全局与上下文配置的定义，使用统一的 `ConfigSpec`：

```python
class ConfigSpec(ValueObject):
    """Specification of a configuration object (Global or Context)."""
    class_name: PascalString | None = None       # 类名，如 "AppSettings" 或 "AuthSettings"
    env_prefix: str = ""                         # 环境变量前缀
    env_file: str | None = None                  # 默认值：Global为".env"，Context为None
    fields: list[ConfigFieldSpec] = Field(default_factory=list)

```

#### 2.3 生成代码结构示例

**`src/context_a/config.py` (定义结构)**：

```python
from pydantic_settings import BaseSettings

class ContextASettings(BaseSettings):
    db_url: str
    pool_size: int = 10

```

**`src/bootstrap/config.py` (聚合加载)**：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from codegen.context_a.config import ContextASettings

class AppSettings(BaseSettings):
    # 全局字段
    debug: bool = False
    
    # 聚合子上下文配置 (Nest)
    context_a: ContextASettings = ContextASettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"  # 支持 APP__CONTEXT_A__DB_URL 这种层级变量
    )

```

### 3. Container 按上下文拆分

#### 3.1 目标目录结构

```
src/codegen/
├── bootstrap/
│   ├── __init__.py
│   ├── config.py                       # Aggregate Config (AppSettings)
│   └── container.py                    # RootContainer (Composition Root)
├── shared/
│   ├── container.py                    # SharedContainer
├── domain_definition/
│   ├── config.py                       # DomainDefinitionSettings
│   ├── container.py                    # DomainDefinitionContainer
│   └── ...
└── orchestration/
    ├── config.py                       # OrchestrationSettings
    ├── container.py                    # OrchestrationContainer
    └── ...

```

#### 3.2 依赖注入流程

**`bootstrap/container.py` (Root Container)：**

```python
class RootContainer(containers.DeclarativeContainer):
    """Root DI Container — Composition Root."""

    # 1. Load Aggregate Configuration
    config = providers.Singleton(AppSettings)

    # 2. Shared Container
    shared = providers.Container(
        SharedContainer,
        config=config,  # Shared 可能需要全局 config
    )

    # 3. Sub-Containers
    # 注意：这里我们只传入上下文相关的配置分片，保持最小知识原则
    domain_definition = providers.Container(
        DomainDefinitionContainer,
        config=config.domain_definition,  # 仅注入 DomainDefinitionSettings
        shared=shared,
    )

```

### 4. 代码生成策略

#### 4.1 生成流程扩展

当执行 `codegen build` 时：

1. **Context 阶段**：
* 遍历所有 Context，若 `context.config` 存在，生成 `{context}/config.py`。
* 生成 `{context}/container.py`，根据 Port/Adapter 绑定自动推导 Providers。


2. **Bootstrap 阶段**：
* 生成 `bootstrap/config.py`：导入所有生成的 Context Config 类，构建 `AppSettings`。
* 生成 `bootstrap/container.py`：导入所有 Context Container，构建 `RootContainer` 并建立层级注入关系。



#### 4.2 BootstrapGenerator

引入专用的 `GenerateBootstrap` 逻辑（整合在 `GenerateProject` UseCase 中），直接消费 Blueprint 全局视图，不依赖现有的 Mapper 体系。

---

## Consequences

### Positive

* **高内聚低耦合**：Context 定义自己的配置，Bootstrap 负责组装，职责分明。
* **运维友好**：单一 `.env` 文件管理所有配置，支持嵌套结构（`ENV_PREFIX__FIELD`）。
* **类型安全**：完全基于 Pydantic，提供运行时的配置验证。
* **标准 DI**：使用 standard dependency-injector 模式，易于测试和扩展。

### Negative

* **生成逻辑复杂**：Bootstrap 生成器需要知道所有 Context 的 Config 类名和路径，增加了模板的复杂度。
* **命名冲突风险**：聚合配置时需确保各 Context 的配置字段名（在 AppSettings 中）不冲突。

### Risks

* **循环依赖**：需严格保证 `bootstrap` 依赖 `context`，而 `context` 绝不反向依赖 `bootstrap`。

```