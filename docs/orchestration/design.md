# Orchestration (编排) 上下文设计文档

## 1. 战略与通用语言 (Strategic & Ubiquitous Language)

### 1.1 核心职责与愿景
作为 Codegen 工具的“总指挥”，Orchestration 上下文负责协调多个限界上下文（DomainDefinition、PythonGen）之间的协作，将用户意图（CLI/MCP 命令）转化为具体的跨上下文业务流程，并提供统一的构建结果。
**核心约束**：本上下文只做“编排”，不做“执行”。

### 1.2 通用语言词汇表
| 业务术语 | 英文对照 | 核心定义 |
| --- | --- | --- |
| **构建结果** | BuildResult | 整个代码生成事务的最终一致性边界，负责汇聚所有文件的生成状态与统计信息。 |
| **文件结果** | FileResult | 记录单个文件的处理路径与状态（Created/Updated/Skipped/Failed）。 |
| **用例编排** | Use Case Orchestration | 跨上下文调用的事务控制单元，如 `GenerateProject` 和 `GenerateBlueprint`。 |

---

## 2. 架构决策记录 (Architecture Decision Records - ADR)

### ADR-001: 移除 Mapper 服务，全面拥抱充血模型
* **背景**：早期设计中使用独立的 `TestSkeletonMapper` 和服务层来处理模型转换，导致贫血模型，且业务逻辑泄露到了 Orchestration 层。
* **决策**：废弃 Mapper 模式，要求 DomainDefinition 上下文的 `Blueprint` 对象提供 `to_package_spec()` 和 `from_package_spec()` 方法，自行完成向 PythonGen 模型的双向映射。
* **影响**：Orchestration 彻底回归纯粹的“编排调度”职责，不再包含具体的领域转换逻辑。

### ADR-002: 接口层的 CQRS (命令与查询分离) 模式
* **背景**：CLI/MCP 传入的操作具有极强的非对称性：构建代码是重度写操作（Command），逆向解析是重度读操作（Query）。
* **决策**：应用层严格实施 CQRS。`GenerateProject` 负责产生系统副作用（生成文件），而 `GenerateBlueprint` 负责读取代码包并写回 YAML（系统代码树不变）。

---

## 3. 核心算法与复杂业务流转 (Tactical Visualization)

### 3.1 核心用例双向流转编排图
*注：展示 Orchestration 是如何串联 DomainDefinition 与 PythonGen 完成正反向工程的。*

```mermaid
graph TD
    subgraph 用户接口层
        CLI[CLI / MCP Server]
    end

    subgraph Orchestration 上下文 应用层编排
        CMD_BUILD[Command: GenerateProject]
        CMD_REV[Command: GenerateBlueprint]
    end

    subgraph 下游基础设施执行 被编排方
        DD_LOAD(DomainDefinition<br/>加载蓝图)
        DD_SAVE(DomainDefinition<br/>保存蓝图)
        PY_GEN(PythonGen<br/>生成源码)
        PY_PARSE(PythonGen<br/>逆向解析)
    end

    CLI -->|codegen build| CMD_BUILD
    CLI -->|codegen reverse| CMD_REV

    %% 正向工程流转
    CMD_BUILD -->|1. 加载 YAML| DD_LOAD
    DD_LOAD -. Blueprint 自身映射 .-> Spec[PackageSpec]
    CMD_BUILD -->|2. 下发 Spec 生成| PY_GEN

    %% 逆向工程流转
    CMD_REV -->|1. 解析 Python 包| PY_PARSE
    PY_PARSE -. PackageSpec 自身映射 .-> BP[Blueprint]
    CMD_REV -->|2. 覆盖保存 YAML| DD_SAVE