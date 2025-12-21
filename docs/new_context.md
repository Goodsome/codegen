你的直觉非常敏锐，这个判断在架构演进中是一个关键的里程碑。

你现在面临的转变，实际上是将项目从一个 **“基于模板的代码脚手架工具”** 升级为一个 **“基于中间表示（IR）的编译器/转译器”**。

在编译器架构中，这对应着 **前端（Frontend，解析语义）** 和 **后端（Backend，生成目标代码）** 的分离。

我的意见是：**非常支持拆分，且现在是最佳时机。**

以下是详细的架构分析和重构建议：

### 1. 为什么要拆分？

当你引入 `ClassSpec` 并试图统一处理 `Aggregate`、`Service` 等概念时，你的模型实际上发生了维度的跳跃：

* **原上下文 (`DomainDefinition`)**：关注的是 **业务语义**。
* 核心词汇：`BoundedContext`, `Aggregate`, `Entity`, `UseCase`, `Repository`.
* 关注点：由于是 DDD 工具，它只关心“这是不是一个聚合根？”，不关心“它是不是一个 Python 类”。


* **新上下文 (`PythonRendering` 或 `CodeStructure`)**：关注的是 **语言特性**。
* 核心词汇：`ClassSpec`, `File`, `Module`, `Import`, `Decorator`, `Method`, `TypeHint`.
* 关注点：它关心“如何组织 imports”，“如何加 `@dataclass` 装饰器”，不关心这个类原本是聚合还是值对象。



如果不拆分，你的 `Aggregate` 对象里会混入大量 `imports`、`decorators` 等与 DDD 无关但与 Python 强相关的字段，导致模型被污染。

### 2. 新的上下文架构设计

建议将系统拆分为两个核心限界上下文，并通过一个 **转换层 (Translator/Mapper)** 连接。

#### Context A: `DomainDefinition` (保持纯净)

这是你目前的 `core`，它代表了 DDD 的蓝图。

* **Aggregate Root**: `Blueprint`
* **职责**：解析 YAML，校验 DDD 规则（例如：聚合根必须有 ID，Repository 只能操作聚合根）。
* **变化频率**：低。

#### Context B: `PythonGen` (新的上下文)

这是专门处理 Python 语言特性的上下文。

* **Aggregate Root**: `SourceFile` (源代码文件) 或 `PythonPackage`。
* **Value Objects**: `ClassSpec`, `FunctionSpec`, `ImportSpec`, `DecoratorSpec`.
* **职责**：负责组装符合 Python 语法的结构，计算依赖引用，渲染最终文本。
* **变化频率**：高（当你调整代码风格、框架依赖时修改这里）。

### 3. 如何解决你的具体痛点？

#### A. 统一为 ClassSpec

在 Context B 中，你不再区分 Aggregate 和 Service。

* Context A 的 `Aggregate` -> 映射为 -> Context B 的 `ClassSpec` (带有 `@dataclass`, `id` 字段)。
* Context A 的 `Service` -> 映射为 -> Context B 的 `ClassSpec` (带有普通方法)。

#### B. 处理 Import 语句

这是拆分后最大的红利。
在 `ClassSpec` 中，你可以定义属性的类型为“强类型对象”。

* **Before**: 模板里硬编码 `from typing import List`.
* **After**:
1. 你定义属性 `type="List[UserId]"`.
2. Context B 的领域服务 `ImportResolver` 扫描所有的 `ClassSpec`。
3. 发现 `List` -> 自动添加 `from typing import List`.
4. 发现 `UserId` -> 自动计算相对路径 -> 添加 `from .value_objects import UserId`.



#### C. 代码反向生成 YAML & 增量更新

这需要你的模型具备“读写能力”。

* **反向生成**：你需要一个 `PythonParser` (适配器)，读取 `.py` 文件，转换成 Context B 的 `ClassSpec`，再尝试推断回 Context A 的 `Aggregate` (这步比较难，通常需要注解辅助)。
* **增量更新**：
1. 读取现有文件 -> 生成 `ClassSpec (Old)`.
2. 根据 YAML -> 生成 `ClassSpec (New)`.
3. **Diff 算法**：对比两个 `ClassSpec`。
4. 策略：保留旧代码中的自定义方法，更新字段定义。
5. 这种逻辑如果写在 Jinja2 模板里是做不到的，必须在对象层面 (`ClassSpec`) 做 Diff。



### 4. 建议的 YAML 调整

你的 `codegen.yaml` 将会演变成这样（描述两个上下文）：

```yaml
contexts:
  # 上下文 1: 定义 DDD 语义
  - name: domain_definition
    description: "Parses the codegen.yaml blueprint."
    domain:
      aggregates:
        - name: Blueprint
          # ... 保持原有的业务定义 ...

  # 上下文 2: 定义 Python 代码结构
  - name: python_gen
    description: "Models the structure of Python code."
    domain:
      aggregates:
        - name: SourceFile
          description: "Represents a single .py file."
          attributes:
            - { name: path, type: str }
            - { name: classes, type: "List[ClassSpec]" }
            - { name: functions, type: "List[FunctionSpec]" }
            - { name: imports, type: "List[ImportSpec]" }
      
      value_objects:
        - name: ClassSpec
          attributes:
            - { name: name, type: str }
            - { name: decorators, type: "List[str]" }
            - { name: bases, type: "List[str]", description: "Inheritance" }
            - { name: attributes, type: "List[FieldSpec]" }
            - { name: methods, type: "List[MethodSpec]" }

      services:
        - name: ImportResolver
          description: "Calculates required imports based on types used in ClassSpecs."
        
        - name: CodeRenderer
          description: "Renders SourceFile object to string (using simple templates)."

    application:
      use_cases:
        - name: TranspileBlueprint
          description: "Converts DomainDefinition Blueprint to PythonGen SourceFiles."
          depends_on_services: [ImportResolver]

```

### 5. 总结与下一步

你的直觉完全正确。**统一 ClassSpec 是这一步的关键，而将它放入独立的上下文是实现“智能生成”（处理 import、增量更新）的基础。**

**新的生成流程将变成：**

1. **Parse**: YAML -> `Blueprint` (Context A)
2. **Translate**: `Blueprint` -> `List[SourceFile]` (Context B, 包含 `ClassSpec`)
* *这里发生逻辑转换，比如给 Aggregate 加上仓储接口定义*


3. **Resolve**: `SourceFile` -> 自动补全 `imports` (Context B Service)
4. **Render**: `SourceFile` -> 写入磁盘 (Infrastructure)

**Would you like me to draft the `ClassSpec` definition in Python specifically tailored to handle the "incremental update" requirement?** (e.g., how to distinguish generated code from user-written code).