# Codegen 全局架构设计文档 (System Architecture)

## 1. 战略愿景与全局原则
Codegen 是一个基于 Python 的 CLI 工具，旨在提供完全由 Agent 驱动的代码脚手架能力。
它采用严格的**领域驱动设计 (DDD)** 结合 **CQRS** 架构，并以 `codegen.yaml` 作为整个系统的**单一事实来源 (SSOT)**。

**核心架构原则**：
1. **基础设施下沉**：核心领域层绝对纯净，所有底层操作（AST操作、文件读写、Jinja渲染）必须通过端口隔离。
2. **状态单一化**：Markdown 设计文档仅用于高维业务决策，不维护结构化字段，彻底消灭双写灾难。
3. **Agentic 友好**：架构设计与模块拆分必须充分考虑 LLM 的上下文窗口大小与任务分解能力（如多米诺骨牌式串行开发）。

## 2. 全局通用语言 (Global Ubiquitous Language)
| 业务术语 | 英文对照 | 核心定义 |
| --- | --- | --- |
| **蓝图** | Blueprint | `codegen.yaml` 文件的内存态表示，驱动所有代码生成逻辑的唯一元模型。 |
| **单一事实来源** | SSOT | Single Source of Truth，特指在本作中所有的类结构、字段、不变量规则均只存在于 YAML 中。 |
| **智能体测试驱动** | Agentic TDD | 通过生成携带 `NotImplementedError` 的测试活文档，触发 Agent (Vibe Coder) 进行确定性补全的开发范式。 |

## 3. 全局限界上下文映射 (Context Map)
*注：展示 Codegen 系统中各独立上下文的逻辑边界与集成模式。*

```mermaid
graph TB
    subgraph "Codegen System Context Map"
        direction TB

        subgraph "Shared Kernel"
            SHARED[Shared<br/>共享内核: 工具类/基础原语]
        end

        subgraph "Core Domain"
            DD[DomainDefinition<br/>领域定义: 维护 YAML 的 SSOT]
        end

        subgraph "Downstream Domains"
            ORCH[Orchestration<br/>编排: 调度各个上下文的业务流转]
            PY[PythonGen<br/>代码生成: 高保真 AST 双向解析与渲染]
        end

        DD -->|使用| SHARED
        ORCH -->|使用| SHARED
        PY -->|使用| SHARED
        
        ORCH -->|Open Host Service (用例调度)| DD
        DD -.->|Conformist (顺从者 / 模型自我转换)| PY
    end
```

## 4. 全局架构决策记录 (Global ADR)

### ADR-001: 确立 codegen.yaml 为唯一真实数据源 (SSOT)
* **背景**：早期在 Markdown 设计文档和 YAML 蓝图中存在大量冗余的字段与规则定义，导致 AI Agent 和人类开发者陷入“双写”状态不同步的灾难。
* **决策**：全面缩减 Markdown 文档，将其转型为仅记录高维决策与算法的“战略图纸”；将实体、值对象、领域服务及 BDD 规则 (rules) 全部下沉到 `codegen.yaml` 中。
* **影响**：极大降低了 LLM 的 Context Token 消耗，提高了开发的确定性。

### ADR-002: BDD 测试驱动架构 (Agentic TDD)
* **背景**：如何让 AI 稳定地实现复杂的底层业务逻辑。
* **决策**：在 YAML 中引入 `given/when/then` 的 rules 节点。Codegen 工具直接生成 `test_*.py` 和带有 `NotImplementedError` + `match-case` 路由的 `bindings_*.py`，利用测试报错驱动 Agent 进行填空式开发。
