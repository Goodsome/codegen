# ADR: Bootstrap 标准化设计

## Status

**Proposed** | 2026-02-16

## Context

Codegen 项目是一个符合 DDD 的标准代码骨架生成器。当前 Bootstrap 层存在以下问题：

### 现状问题

1. **BootstrapSpec 元模型过于简陋**：当前 `codegen.yaml` 中的 `BootstrapSpec` 仅有 `bindings: list[PortBinding]`，无法描述容器层级结构和配置定义。
2. **Container 扁平化**：`src/codegen/bootstrap.py` 中只有一个 `Container` 类，全部四个上下文（DomainDefinition, Orchestration, PythonGen, Shared）的依赖混杂在一起，违反了 Bounded Context 的边界隔离原则。
3. **Config 原始化**：配置以 `providers.Configuration()` 字典形式分散定义，缺乏类型安全和环境隔离能力。
4. **Mapper 体系缺失**：`Orchestration` 上下文中的 Mapper 体系没有 Bootstrap 相关的映射器，无法将 BootstrapSpec 元模型映射为可生成的代码结构。

### 关联 User Story

- Ref: `docs/stories/S260216_bootstrap_and_interfaces.md`

---

## Decision

### 1. BootstrapSpec 元模型扩展

#### 1.1 设计原则

BootstrapSpec 作为 `DomainDefinition` 上下文中的值对象，负责 **描述** Bootstrap 层的结构。遵循以下原则：

- **声明式而非命令式**：BootstrapSpec 只描述 "有什么"、"怎么组合"，不包含实现逻辑
- **层级化而非扁平化**：支持 Root Container 和 Context Container 的层级结构
- **可选扩展**：各节点均为可选，渐进式采用

#### 1.2 新版 BootstrapSpec 结构

扩展后的 Blueprint 顶层 `bootstrap` 节点从仅有 `bindings` 升级为完整的引导配置规格：

```yaml
# codegen.yaml 中的 bootstrap 节（顶层）
bootstrap:
  config:                     # GlobalConfig 定义
    class_name: AppSettings   # 生成的类名，默认 "{ProjectName}Settings"
    env_prefix: ""            # pydantic_settings 的 env_prefix
    env_file: ".env"          # 默认 .env 文件路径
    fields:                   # 全局配置字段列表
      - name: debug
        type: bool
        default: "false"
      - name: log_level
        type: str
        default: '"INFO"'

  bindings:                   # 保留现有的 Port-Adapter 绑定
    - port: BlueprintStorage
      implementation: YamlBlueprintStorage

  container:                  # RootContainer 定义（可选，用于描述额外 providers）
    providers: []             # 未来可扩展的额外全局 providers
```

#### 1.3 BoundedContext 扩展

在 `BoundedContext` 中新增 `config` 和 `container` 可选节点：

```yaml
# codegen.yaml 中的 BoundedContext 扩展
- name: SomeContext
  config:                     # Context 级配置（可选）
    class_name: SomeContextSettings
    env_prefix: "SOME_CTX_"
    fields:
      - name: api_endpoint
        type: str
        default: '"http://localhost:8080"'
  container:                  # Context Container 额外定义（可选）
    providers: []             # UseCase/Service/Repository 的绑定自动从 application + infrastructure 推导
  domain: ...
  application: ...
  infrastructure: ...
```

#### 1.4 元模型值对象定义

在 `DomainDefinition` 上下文中需新增/修改以下值对象：

| 值对象 | 描述 | 位置 |
|--------|------|------|
| `BootstrapSpec` | 顶层引导规格（**修改现有**） | `DomainDefinition.domain.value_objects` |
| `GlobalConfigSpec` | 全局配置定义 | `DomainDefinition.domain.value_objects` |
| `ContextConfigSpec` | 上下文级配置定义 | `DomainDefinition.domain.value_objects` |
| `ConfigFieldSpec` | 配置字段定义 | `DomainDefinition.domain.value_objects` |
| `ContainerSpec` | 容器额外定义（预留扩展） | `DomainDefinition.domain.value_objects` |

**BootstrapSpec（修改后）：**

```python
class BootstrapSpec(ValueObject):
    """Specification of the bootstrap configuration."""
    bindings: list[PortBinding] = Field(default_factory=list)
    config: GlobalConfigSpec | None = None
    container: ContainerSpec | None = None
```

**GlobalConfigSpec（新增）：**

```python
class GlobalConfigSpec(ValueObject):
    """Specification of the global configuration using pydantic_settings."""
    class_name: PascalString | None = None       # 默认 "{ProjectName}Settings"
    env_prefix: str = ""
    env_file: str = ".env"
    fields: list[ConfigFieldSpec] = Field(default_factory=list)
```

**ContextConfigSpec（新增）：**

```python
class ContextConfigSpec(ValueObject):
    """Specification of a bounded context's configuration."""
    class_name: PascalString | None = None       # 默认 "{ContextName}Settings"
    env_prefix: str = ""
    fields: list[ConfigFieldSpec] = Field(default_factory=list)
```

**ConfigFieldSpec（新增）：**

```python
class ConfigFieldSpec(ValueObject):
    """Specification of a configuration field."""
    name: SnakeString
    type: str                    # Python 类型注解字符串
    default: str | None = None   # 默认值（字符串形式）
    description: str = ""
    env_var: str | None = None   # 可覆盖的环境变量名
```

**ContainerSpec（新增，预留扩展）：**

```python
class ContainerSpec(ValueObject):
    """Specification of container-level customizations."""
    providers: list[ProviderSpec] = Field(default_factory=list)
    # 未来可扩展：overrides, scopes, etc.
```

**BoundedContext（修改后）：**

```python
class BoundedContext(ValueObject):
    """A logical boundary within the system."""
    name: PascalString
    description: str = Field(default_factory=str)
    config: ContextConfigSpec | None = None          # 新增
    container: ContainerSpec | None = None            # 新增
    domain: DomainSpec = Field(default_factory=DomainSpec)
    application: ApplicationSpec = Field(default_factory=ApplicationSpec)
    infrastructure: InfrastructureSpec = Field(default_factory=InfrastructureSpec)
```

---

### 2. 代码生成策略

#### 2.1 目标目录结构

生成后的项目目录结构如下（以 Codegen 项目自身为例）：

```
src/codegen/
├── bootstrap/                          # Bootstrap 层（Root）
│   ├── __init__.py
│   ├── config.py                       # GlobalConfig (pydantic_settings.BaseSettings)
│   └── container.py                    # RootContainer (DeclarativeContainer)
├── shared/
│   ├── container.py                    # SharedContainer
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── domain_definition/
│   ├── container.py                    # DomainDefinitionContainer
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── orchestration/
│   ├── container.py                    # OrchestrationContainer
│   ├── domain/
│   ├── application/
│   └── infrastructure/
└── python_gen/
    ├── container.py                    # PythonGenContainer
    ├── domain/
    ├── application/
    └── infrastructure/
```

#### 2.2 Config 代码生成模板

**`bootstrap/config.py`：**

```python
# AUTO-GENERATED by codegen — DO NOT EDIT
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Global application settings."""

    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = ""
```

**Context 级 Config（如 `domain_definition/config.py`）：**

```python
# AUTO-GENERATED by codegen — DO NOT EDIT
from pydantic_settings import BaseSettings


class DomainDefinitionSettings(BaseSettings):
    """DomainDefinition context settings."""

    some_setting: str = "default"

    class Config:
        env_prefix = "DD_"
```

生成规则：
- 仅当 `bootstrap.config` 被定义时生成 `bootstrap/config.py`
- 仅当 `BoundedContext.config` 被定义时生成 `{context}/config.py`
- 字段直接映射为 `BaseSettings` 的类属性
- `model_config` 使用 `SettingsConfigDict` (Pydantic v2 风格)

#### 2.3 Container 代码生成模板

**`{context}/container.py` (Context Container)：**

```python
# AUTO-GENERATED by codegen — DO NOT EDIT
from dependency_injector import containers, providers

# 自动导入该上下文的 Use Case、Port、Adapter
from codegen.domain_definition.application.use_cases.load_blueprint import LoadBlueprint
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.infrastructure.adapters.yaml_blueprint_storage import YamlBlueprintStorage


class DomainDefinitionContainer(containers.DeclarativeContainer):
    """DI Container for DomainDefinition bounded context."""

    # --- Injected Dependencies (由 Root Container 提供) ---
    config = providers.Configuration()
    shared = providers.DependenciesContainer()          # 引用 SharedContainer

    # --- Infrastructure Adapters (根据 bindings 生成) ---
    blueprint_storage = providers.Singleton(YamlBlueprintStorage, config=config)

    # --- Application Use Cases (根据 use_cases + dependencies 自动推导) ---
    load_blueprint = providers.Factory(
        LoadBlueprint,
        blueprint_loader=blueprint_storage,
    )
```

**`bootstrap/container.py` (Root Container)：**

```python
# AUTO-GENERATED by codegen — DO NOT EDIT
from dependency_injector import containers, providers

from codegen.bootstrap.config import AppSettings
from codegen.shared.container import SharedContainer
from codegen.domain_definition.container import DomainDefinitionContainer
from codegen.orchestration.container import OrchestrationContainer
from codegen.python_gen.container import PythonGenContainer


class RootContainer(containers.DeclarativeContainer):
    """Root DI Container — Composition Root."""

    # --- Global Configuration ---
    config = providers.Singleton(AppSettings)

    # --- Sub-Containers (按 Bounded Context 拆分) ---
    shared = providers.Container(
        SharedContainer,
        config=config,
    )

    domain_definition = providers.Container(
        DomainDefinitionContainer,
        config=config,
        shared=shared,
    )

    orchestration = providers.Container(
        OrchestrationContainer,
        config=config,
        shared=shared,
        domain_definition=domain_definition,
    )

    python_gen = providers.Container(
        PythonGenContainer,
        config=config,
        shared=shared,
    )
```

生成规则：
- 每个 `BoundedContext` 自动生成 `{context_name}/container.py`
- Root Container 自动将所有 Context Container 组合为 `providers.Container()`
- Port → Adapter 绑定：
  - 优先从 `BoundedContext` 自身的 `infrastructure.implementations` 查找匹配
  - 全局 `bootstrap.bindings` 作为补充/覆盖
- UseCase 依赖自动从 `use_case.dependencies` 推导，匹配同上下文的 Port/Service Provider

#### 2.4 依赖推导算法

Container Provider 的生成采用以下**自动推导策略**：

1. **收集阶段**：扫描 `BoundedContext` 中的所有组件：
   - `domain.ports` → 声明的端口接口
   - `domain.services` → 领域服务（及其 `dependencies`）
   - `infrastructure.implementations` → 适配器实现
   - `application.use_cases` → 用例（及其 `dependencies`）

2. **绑定阶段**：建立 Port → Implementation 映射：
   - 首先从 `infrastructure.implementations[].implements` 字段匹配
   - 然后搜索 `bootstrap.bindings` 进行覆盖或跨上下文绑定

3. **Provider 生成阶段**：按拓扑顺序生成：
   - Shared Port Implementations → `providers.Singleton`
   - Domain Services → `providers.Singleton`（注入依赖项）
   - Use Cases → `providers.Factory`（注入 Port 和 Service）

4. **跨上下文依赖处理**：
   - 如果 UseCase 的 `dependency.type` 指向另一个上下文的 UseCase 或 Port，则通过 `providers.DependenciesContainer()` + Root Container 注入解决

---

### 3. Mapper 体系影响评估

#### 3.1 当前 Mapper 体系概览

```
BlueprintMapper
  └── ContextMapper
       ├── DomainMapper
       │    ├── AggregateMapper
       │    ├── EntityMapper
       │    ├── ValueObjectMapper
       │    ├── ServiceMapper
       │    ├── PortMapper
       │    └── EnumMapper
       ├── ApplicationMapper
       │    ├── UseCaseMapper
       │    └── PortMapper
       └── InfrastructureMapper
            └── ImplementationMapper
```

#### 3.2 Bootstrap 是否需要 Mapper？

**结论：暂不引入 BootstrapMapper。**

**理由：**

| 考量维度 | 分析 |
|----------|------|
| **映射方向** | 当前 Mapper 负责 `DDD Spec ↔ Python AST (PackageSpec)` 的双向映射。Bootstrap 层的 Container 代码结构（`DeclarativeContainer`）与 PackageSpec 中的 `ClassSpec` 差异显著，强行映射会导致大量特殊处理。 |
| **生成复杂度** | Container 代码的生成需要跨上下文的全局信息（Port 绑定、UseCase 依赖图），而当前 Mapper 体系是按上下文隔离的逐层映射，无法自然获取跨上下文信息。 |
| **Reverse 需求** | Bootstrap/Container 代码几乎不会被 reverse engineer 回 `codegen.yaml`，因此不需要 `to_bootstrap_spec()` 方向的映射。 |
| **替代方案** | 更适合采用 **专用 Generator（生成器）** 模式：`BootstrapGenerator` 直接消费 `Blueprint`（包含所有上下文和 BootstrapSpec），生成 Container/Config 文件。这是一种 **单向转换**，不需要双向映射能力。 |

#### 3.3 推荐方案：BootstrapGenerator

在 `Orchestration` 上下文的 `application` 层引入新的 UseCase 或 Service：

```
Orchestration
  └── application
       └── use_cases
            ├── GenerateProject        # 已有，负责整体生成
            ├── GenerateBlueprint      # 已有，负责 Blueprint 反向
            └── GenerateBootstrap      # 新增，专门负责 Bootstrap 层生成
```

或者，将 Bootstrap 生成逻辑整合进现有的 `GenerateProject` UseCase 中，作为额外的生成步骤。

**推荐做法**：整合进 `GenerateProject`，理由：
- Bootstrap 层是项目生成的一部分，不应独立触发
- `GenerateProject` 已经拥有 `Blueprint` 全局视图
- 保持用户命令的简洁性（一个 `codegen build` 搞定一切）

#### 3.4 BlueprintMapper 兼容性

`BlueprintMapper.to_package_spec()` 当前只映射 `contexts[]`，不处理 `bootstrap` 节点。这是正确的——因为 Bootstrap 生成走专用路径，不经过 PackageSpec 中间表示。

因此，**现有 Mapper 体系无需修改**。

---

### 4. 配置管理详细设计

#### 4.1 技术选型

| 项 | 选择 | 理由 |
|----|------|------|
| 配置基类 | `pydantic_settings.BaseSettings` | 类型安全、自动 .env 读取、验证 |
| 容器集成 | `providers.Singleton(AppSettings)` | 配置全局唯一，通过 DI 注入 |
| 环境隔离 | `env_prefix` + `.env` 文件 | 开发/测试/生产环境隔离 |

#### 4.2 Pydantic v2 风格

生成的 Config 代码应使用 Pydantic v2 的 `model_config` 风格：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )

    debug: bool = False
    log_level: str = "INFO"
```

#### 4.3 配置注入流程

```
                 .env / ENV VARS
                       │
                       ▼
              ┌─────────────────┐
              │   AppSettings   │  (pydantic_settings)
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  RootContainer  │
              │  config = ...   │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌────────────┐ ┌─────────┐ ┌─────────┐
   │CtxA Cont.  │ │CtxB ... │ │Shared   │
   │config=root │ │         │ │Container│
   │  .config   │ │         │ │         │
   └────────────┘ └─────────┘ └─────────┘
```

---

### 5. 生成时机与命令集成

#### 5.1 `codegen build` 行为扩展

当用户执行 `codegen build` 时，`GenerateProject` UseCase 的执行流程扩展为：

```
1. Load Blueprint (codegen.yaml)
2. For each BoundedContext:
   a. Generate domain/ (现有)
   b. Generate application/ (现有)
   c. Generate infrastructure/ (现有)
   d. Generate container.py (新增)
   e. Generate config.py (新增，仅当 context.config 存在时)
3. Generate bootstrap/config.py (新增，仅当 bootstrap.config 存在时)
4. Generate bootstrap/container.py (新增)
```

#### 5.2 Overwrite 策略

Bootstrap 层文件的 overwrite 策略与现有一致：
- 默认不覆盖（`--overwrite` / `node` 模式控制）
- Container 文件作为**骨架代码**，用户可在其上添加自定义 Provider
- Config 文件作为**纯声明式**代码，始终可安全重新生成

---

### 6. 实现路线图

#### Phase 1: 元模型扩展 (codegen.yaml + ValueObjects)

1. 在 `codegen.yaml` 的 `DomainDefinition` 上下文中新增值对象：
   - `GlobalConfigSpec`, `ContextConfigSpec`, `ConfigFieldSpec`, `ContainerSpec`
2. 修改 `BootstrapSpec`：添加 `config` 和 `container` 属性
3. 修改 `BoundedContext`：添加 `config` 和 `container` 属性
4. 执行 `codegen build` 重新生成元模型代码

#### Phase 2: 代码生成实现

1. 在 `PythonGen` 上下文中实现 Bootstrap 代码生成模板（Jinja2）
2. 在 `Orchestration` 上下文中扩展 `GenerateProject` UseCase
3. 实现依赖推导算法
4. 集成到 `codegen build` 流程

#### Phase 3: 现有代码迁移

1. 将现有的 `src/codegen/bootstrap.py` 拆分为目标结构
2. 为 Codegen 自身项目定义 Bootstrap 配置
3. 验证生成结果与手写代码的等价性

---

## Consequences

### Positive

- **类型安全**：配置通过 `BaseSettings` 获得完整的类型检查和验证
- **上下文隔离**：每个 Bounded Context 拥有自己的 Container，遵循 DDD 边界
- **自动化**：Container 的 Provider 绑定从 Blueprint 自动推导，减少手动配置
- **标准参考**：生成的 Bootstrap 代码可作为 DDD 项目的标准模板
- **渐进式采用**：所有新增节点均为可选，不破坏现有配置

### Negative

- **复杂度增加**：元模型的值对象数量增加，Blueprint 理解成本上升
- **生成逻辑复杂**：跨上下文的依赖推导算法需要全局视图，增加了 `GenerateProject` 的逻辑复杂度
- **定制性限制**：自动推导的 Container 可能不满足复杂场景，需要保留手动调整能力

### Risks

- **依赖推导准确性**：自动推导可能遗漏边界情况（如同名 Port 跨上下文等），需要充分测试
- **向后兼容**：`BootstrapSpec` 的扩展需要确保旧版 `codegen.yaml`（仅有 `bindings`）仍然可以正常加载

---

## References

- User Story: `docs/stories/S260216_bootstrap_and_interfaces.md`
- 现有 Bootstrap: `src/codegen/bootstrap.py`
- dependency-injector 文档: https://python-dependency-injector.ets-labs.org/
- pydantic-settings 文档: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
