这是一个非常符合 DDD 战略设计（Strategic Design）的决策。

当两个限界上下文（Bounded Context）之间存在直接的模型转化和协作流时，如果不希望它们相互耦合（例如 `domain_definition` 不应该知道 `python_gen` 的存在），在它们之上建立一个 **Orchestration（编排层）** 或者称为 **Application Layer (System Level)** 是最佳实践。

根据你的 `codegen.yaml` 和需求，我建议 `src/codegen/orchestration` 的目录结构如下：

### 推荐的目录结构

```text
src/codegen/orchestration/
├── __init__.py
├── translators/                  # 核心职责：上下文映射 (Context Mapping/ACL)
│   ├── __init__.py
│   ├── base.py                   # 定义转化接口
│   └── blueprint_to_python.py    # 实现 Blueprint -> PackageSpec 的转化逻辑
├── workflows/                    # 核心职责：业务流程编排 (Sagas/Workflows)
│   ├── __init__.py
│   └── project_generation.py     # 串联 "Load -> Translate -> Generate" 的全流程
└── cli/                          # (可选) 如果编排层直接作为入口，可放置 CLI 命令
└── main.py
```

---

### 详细设计说明

#### 1. `translators/` (转化层 / 防腐层)

这是你最关心的部分。这一层负责将 **源上下文模型** 映射为 **目标上下文模型**。在 DDD 中，这通常被称为 ACL (Anti-Corruption Layer) 或者 Context Mapper。

*   **目的**：保持 `domain_definition` 和 `python_gen` 的纯洁性。它们不需要知道彼此的存在。
*   **代码示例 (`blueprint_to_python.py`)**:

```python
from typing import List
# 引入源模型
from codegen.domain_definition.domain.aggregates import Blueprint, MetaAggregate
# 引入目标模型
from codegen.python_gen.domain.aggregates import PackageSpec, ModuleSpec, ClassSpec

class BlueprintToPythonTranslator:
    """
    负责将领域定义层的 Blueprint 转化为 Python生成层的 PackageSpec
    """

    def translate(self, blueprint: Blueprint) -> PackageSpec:
        modules: List[ModuleSpec] = []

        # 1. 遍历 Blueprint 中的聚合，转化为 Python 类/模块
        for context in blueprint.contexts:
            for aggregate in context.domain.aggregates:
                module_spec = self._convert_aggregate_to_module(aggregate)
                modules.append(module_spec)

        # 2. 组装成 PackageSpec
        return PackageSpec(
            path=blueprint.name, # 或者基于 blueprint.xyz 计算路径
            modules=modules
        )

    def _convert_aggregate_to_module(self, aggregate: MetaAggregate) -> ModuleSpec:
        # 具体转化逻辑：把 MetaAggregate 的属性变成 ClassSpec 的字段
        # ...
        pass
```

#### 2. `workflows/` (编排层 / 流程层)

编排层并不包含复杂的业务规则（那是 Domain 的事），也不包含具体的转化逻辑（那是 Translator 的事）。它的职责是**调用**。它像一个指挥家。

*   **职责**：
1.  调用 `domain_definition` 的 Port 读取 Blueprint。
2.  调用 `orchestration.translators` 进行模型转化。
3.  调用 `python_gen` 的 UseCase 进行代码生成。

*   **代码示例 (`project_generation.py`)**:

```python
from codegen.domain_definition.domain.ports import BlueprintLoaderPort
from codegen.python_gen.application.use_cases import GeneratePackage, GeneratePackageCommand
from codegen.orchestration.translators.blueprint_to_package_spec import BlueprintToPythonTranslator


class ProjectGenerationWorkflow:
    def __init__(
            self,
            loader: BlueprintLoaderPort,
            generator: GeneratePackage,
            translator: BlueprintToPythonTranslator
    ):
        self.loader = loader
        self.generator = generator
        self.translator = translator

    def run(self, blueprint_path: str, overwrite: bool = False):
        # Step 1: 从 domain_definition加载蓝图
        blueprint = self.loader.load(blueprint_path)
        if not blueprint:
            raise ValueError("Blueprint not found")

        # Step 2: 在编排层进行转化 (Blueprint -> PackageSpec)
        package_spec = self.translator.execute(blueprint)

        # Step 3: 调用 python_gen 下发生成命令
        command = GeneratePackageCommand(
            package_spec=package_spec,
            overwrite=overwrite
        )
        result = self.generator.execute(command)

        return result
```

### 为什么这样做更好？

1.  **解耦 (Decoupling)**:
*   如果你把转化逻辑放在 `domain_definition` 里，那么"定义层"就不仅仅是定义了，它还得懂 Python 语法，这违反了单一职责。
*   如果你把转化逻辑放在 `python_gen` 里，那么"生成层"就被绑定到了特定的 Blueprint 结构上，它就不能通用于其他输入源（比如从 JSON Schema 生成 Python）。
*   放在 `orchestration`，两个上下文都可以独立演进。

2.  **可测试性 (Testability)**:
*   你可以单独为 `translators/blueprint_to_python.py` 编写单元测试，验证转化逻辑是否正确，而不需要真的去读写文件。

3.  **扩展性 (Extensibility)**:
*   如果未来你还需要支持 `JavaScript` 生成，你只需要增加一个 `python_gen` 的兄弟上下文 `js_gen`，然后在 `orchestration/translators/` 下增加一个 `blueprint_to_js.py` 即可，原有的代码几乎不用动。

### 集成到 yaml 模型中（可选）

虽然目前的 `codegen.yaml` 主要描述的是核心领域模型，但如果你想用 yaml 来生成这个编排层的骨架，你可以把 `orchestration` 当作一个新的（但比较薄的）Context 加上去，或者手动维护这一层。通常编排层属于 System Application Layer，手动维护往往更灵活。