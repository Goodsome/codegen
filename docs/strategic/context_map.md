---
name: Codegen 限界上下文映射图
description: 定义各个上下文之间的边界与协作模式
type: project
---

# 🗺️ 限界上下文映射图 (Context Map)

## 全局上下文映射关系

```mermaid
graph TB
    subgraph "Codegen System Context Map"
        direction TB

        subgraph "Shared Kernel (通用域)"
            SHARED[Shared<br/>共享内核: 工具类/基础原语]
        end

        subgraph "Core Domain (核心域)"
            DD[DomainDefinition<br/>领域定义: 维护 YAML 的 SSOT]
        end

        subgraph "Supporting Domains (支撑域)"
            ORCH[Orchestration<br/>编排: 调度各个上下文的业务流转]
            PY[PythonGen<br/>代码生成: 高保真 AST 双向解析与渲染]
        end

        %% Shared Kernel 依赖关系
        DD -->|使用| SHARED
        ORCH -->|使用| SHARED
        PY -->|使用| SHARED
        
        %% 上下文协作关系
        ORCH -->|Conformist (用例调度)| DD
        ORCH -->|Conformist (用例调度)| PY
        DD -.->|Conformist (顺从者 / 模型自我转换)| PY
    end
```

## 各上下文边界定义

### 1. DomainDefinition (领域定义)
- **边界内职责**：
  - 解析与验证 `codegen.yaml` 蓝图
  - 提供蓝图的 CRUD 操作与路径查询能力
  - 维护领域模型的一致性与业务规则校验
  - 提供模型转换能力，适配下游代码生成器需求
- **对外提供接口**：
  - 蓝图加载/保存服务
  - 命令式更新服务 (AddEntity, AddAttribute 等)
  - 模型转换导出服务
- **对外依赖**：
  - 模型自转换成 PythonGen 的模型

### 2. Orchestration (编排)
- **边界内职责**：
  - 处理 CLI 入口命令路由
  - 处理 MCP 工具请求路由
  - 协调跨上下文的复杂业务流程
  - 对外暴露统一的服务接口
- **对外依赖**：
  - DomainDefinition 上下文的所有服务
  - PythonGen 上下文的代码生成服务

### 3. PythonGen (Python 代码生成)
- **边界内职责**：
  - 将 PackageSpec / ModuleSpec 模型转换为 Python AST 节点
  - 代码生成与文件写入
  - 反向工程：从现有 Python 代码解析成结构化的 PackageSpec
  - 代码格式化与质量保证
- **对外依赖**：
  - Shared Kernel 的工具类支持

### 4. Shared Kernel (共享内核)
- **边界内职责**：
  - 通用工具函数（字符串转换、路径处理等）
  - 基础原语类型（NamingString, SnakeString, PascalString 等）
  - 跨上下文通用的抽象接口定义
- **使用约束**：
  - 禁止在 Shared Kernel 中添加任何业务逻辑
  - 所有修改必须经过全局架构评审
