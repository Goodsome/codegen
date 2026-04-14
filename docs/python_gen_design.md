# PythonGen (代码生成) 上下文设计文档

## 1. 战略与通用语言 (Strategic & Ubiquitous Language)

### 1.1 核心职责与愿景
将结构化领域模型（`PackageSpec`, `ModuleSpec`）与 Python 源代码之间进行高保真的**双向转换**。它既是代码生成器，也是 AST 逆向解析器，同时负责自动处理依赖解析与代码格式化。

### 1.2 通用语言词汇表
| 业务术语 | 英文对照 | 核心定义 |
| --- | --- | --- |
| **包规格** | PackageSpec | PythonGen 的唯一聚合根，代表一个 Python 包及文件树的顶层边界，保证全局符号和文件生成的一致性。 |
| **模块规格** | ModuleSpec | 代表一个 `.py` 文件的元模型，可进行 Merge (合并) 操作。 |
| **源码端口** | SourceCodePort | 隔离具体语法树解析实现（如 Python `ast`）的六边形架构端口。 |
| **依赖解析器** | DependencyResolver | 领域无状态服务，用于在生成代码前，自动补全缺失的 Python `import` 语句。 |

---

## 2. 架构决策记录 (Architecture Decision Records - ADR)

### ADR-001: AST 操作与领域逻辑的端口隔离
* **背景**：直接在领域对象中操作 Python `ast` 节点会导致核心域被底层技术实现污染，且不便于未来迁移（如迁移到 `libcst` 支持保留注释）。
* **决策**：使用标准六边形架构。领域层仅定义 `SourceCodePort`，将所有的 `ast.parse` 和 `ast.unparse` 逻辑下沉至基础设施层的 `AstTranslator` 中。
* **影响**：领域层模型（Spec）变得极其纯粹，仅包含标准的 Python 数据结构。

### ADR-002: 支持增量合并 (Incremental Merge) 的非破坏性生成
* **背景**：代码脚手架在二次生成时极易覆盖用户手写的代码。
* **决策**：在 `GeneratePackage` 流程中，引入 `PackageSpec.merge()` 机制。在写入磁盘前，先通过 `to_package_spec` 将现有代码解析到内存，与新生成的 Spec 进行合并，再进行全量重写。

---

## 3. 核心算法与复杂业务流转 (Tactical Visualization)

### 3.1 内部防腐与六边形架构依赖图
*注：展示 PythonGen 是如何利用端口隔离第三方底层库的。*

```mermaid
graph TD
    subgraph 领域层内核Domain Core
        PKG[PackageSpec <br/> 聚合根]
        TRANS[PythonSyntaxTranslator <br/> 领域服务]
        RESOLVER[DependencyResolver <br/> 依赖推导服务]
        
        PORT_AST((SourceCodePort))
        PORT_FMT((CodeFormatter))
        
        TRANS --> PKG
        TRANS --> RESOLVER
        TRANS --> PORT_AST
        TRANS --> PORT_FMT
    end

    subgraph 基础设施层 Infrastructure Adapters
        AST_ADAPTER[AstTranslator]
        FMT_ADAPTER[BlackCodeFormatter]
    end

    subgraph 第三方技术栈
        LIB_AST[Python standard 'ast']
        LIB_BLACK[Black Formatter]
    end

    PORT_AST -.->|实现| AST_ADAPTER
    PORT_FMT -.->|实现| FMT_ADAPTER
    
    AST_ADAPTER --> LIB_AST
    FMT_ADAPTER --> LIB_BLACK