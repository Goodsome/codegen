# 元模型驱动的测试用例生成标准

## 1. 核心设计理念

本标准基于 **行为驱动开发 (BDD)** 哲学与 **Vibe Coding** 工作流制定，旨在通过确定性的工具约束不确定性的 AI，实现测试代码的极简与高效。
* **单一事实来源 (Single Source of Truth)**：`codegen.yaml` 是系统架构与核心业务规则的唯一事实来源。
* **意图与实现隔离**：测试执行文件（`test_*.py`）只描述“业务意图（What）”，完全自动生成且只读；语义翻译层（`bindings_*.py`）负责“底层实现（How）”，交由 LLM 维护。
* **极简双文件架构**：摒弃复杂的继承体系，采用 `test_*.py` (活文档执行器) + `bindings_*.py` (语义翻译官) 的扁平化设计。
* **函数式驱动**：遵循 Pytest 的最佳实践，放弃臃肿的测试类，采用纯函数式测试与 Fixture 注入。

## 2. YAML 元模型 `rules` 定义规范

业务规则必须在 `codegen.yaml` 的 `use_cases` 或 `behaviors` 或 `operations` 节点下进行定义。工具将直接读取这些纯自然语言描述生成测试的执行流。

**YAML 结构规范：**

```yaml
# codegen.yaml (片段示例：SetValue 用例)
  application:
    use_cases:
    - name: SetValue
      kind: command
      # ... attributes ...
      rules:
        - name: AppendToListSuccessfully
          given: "存储中已存在包含列表的 Blueprint"
          when: "执行 SetValueCommand，append=True"
          then: "存储中的列表末尾新增了该 value，且返回成功状态"
          
        - name: FailWhenAppendingToNonList
          given: "存储中目标路径的值是一个字符串"
          when: "执行 SetValueCommand，append=True"
          then: "抛出 TypeMismatchError 异常"
```

* **架构约束**：如果单一用例/行为下的 `rules` 数量过多，表明该用例权责过重，应考虑进行架构层面的重构与拆分。

## 3. 测试骨架架构模式 (统一 2-File 模式)

测试代码严格划分为两个文件：**全量生成的执行文档** 与 **LLM 维护的语义翻译层**。

### 3.1 测试执行层 (活文档) - 100% 工具生成，禁止手动修改
此文件由 `codegen` 基于 YAML 每次全量覆写生成。它采用 Pytest 推荐的函数式风格，利用 Fixture 注入 Bindings 实例，内部仅包含强类型的 `given/when/then` 语义桩调用。

* **输出位置**: `tests/unit/application/test_set_value.py`

```python
# --- 由 Codegen 自动生成，基于 YAML rules 节点，请勿手动修改 ---
import pytest
from tests.unit.application.bindings_set_value import SetValueBindings

@pytest.fixture
def set_value_bindings() -> SetValueBindings:
    """初始化并注入该用例的语义翻译层"""
    return SetValueBindings()

def test_append_to_list_successfully(set_value_bindings: SetValueBindings):
    """
    [Rule]: AppendToListSuccessfully
    [Desc]: 当 append 为 True 且目标路径已存在列表时，新值应追加到列表末尾。
    """
    (set_value_bindings
        .given("存储中已存在包含列表的 Blueprint")
        .arrange_done()
        .when("执行 SetValueCommand，append=True")
        .then("存储中的列表末尾新增了该 value，且返回成功状态")
    )

def test_fail_when_appending_to_non_list(set_value_bindings: SetValueBindings):
    """
    [Rule]: FailWhenAppendingToNonList
    [Desc]: 当 append 为 True 但目标路径对应的值不是列表时，应抛出类型冲突异常。
    """
    (set_value_bindings
        .given("存储中目标路径的值是一个字符串")
        .arrange_done()
        .when("执行 SetValueCommand，append=True")
        .then("抛出 TypeMismatchError 异常")
    )
```

### 3.2 语义翻译层 (Bindings) - 工具首次生成骨架，LLM 负责翻译填空
此文件包含一个状态机类。Codegen 仅在文件不存在时生成空壳与基础路由。后续由 **Agent / LLM** 根据 `test_*.py` 中报错的未实现语句，利用 Python 的模式匹配（Pattern Matching）路由到**私有方法**中进行具体代码的编写。

* **输出位置**: `tests/unit/application/bindings_set_value.py`

```python
# --- Codegen 首次生成骨架，后续由 LLM 负责编写与维护翻译逻辑 ---
from typing import Any
from codegen.application.use_cases.set_value import SetValueUseCase, SetValueCommand
# (此处省略 fake storage 等基础设施的 import)

class SetValueBindings:
    def __init__(self):
        # 初始化底层的 Fake 依赖与被测对象
        self.storage = FakeYamlBlueprintStorage()
        self.use_case = SetValueUseCase(storage=self.storage)
        self.result: Any = None
        self.exception: Exception | None = None

    # ==========================================
    # 模式匹配路由层 (Pattern Matching Routing)
    # ==========================================
    
    def given(self, semantic_text: str) -> 'SetValueBindings':
        match semantic_text:
            case "存储中已存在包含列表的 Blueprint":
                self._given_existing_list_blueprint()
            case "存储中目标路径的值是一个字符串":
                self._given_existing_string_blueprint()
            case _:
                raise NotImplementedError(f"未实现的 Given 语义: {semantic_text}")
        return self

    def arrange_done(self) -> 'SetValueBindings':
        return self

    def when(self, semantic_text: str) -> 'SetValueBindings':
        match semantic_text:
            case "执行 SetValueCommand，append=True":
                self._when_execute_with_append_true()
            case _:
                raise NotImplementedError(f"未实现的 When 语义: {semantic_text}")
        return self

    def then(self, semantic_text: str) -> 'SetValueBindings':
        match semantic_text:
            case "存储中的列表末尾新增了该 value，且返回成功状态":
                self._then_value_appended_and_success()
            case "抛出 TypeMismatchError 异常":
                self._then_raises_type_mismatch_error()
            case _:
                raise NotImplementedError(f"未实现的 Then 语义: {semantic_text}")
        return self

    # ==========================================
    # 业务实现逻辑层 (Private Implementation Methods)
    # ==========================================
    # LLM 将具体的伪造数据、方法调用与断言逻辑封装在私有方法中，避免 match 语句块过度膨胀
    
    def _given_existing_list_blueprint(self):
        self.storage.seed_data({"contexts.Shared": ["old_item"]})
        
    def _given_existing_string_blueprint(self):
        self.storage.seed_data({"contexts.Shared": "i_am_string"})
        
    def _when_execute_with_append_true(self):
        command = SetValueCommand(path="contexts.Shared", value="new_item", append=True)
        try:
            self.result = self.use_case.execute(command)
        except Exception as e:
            self.exception = e
            
    def _then_value_appended_and_success(self):
        assert self.exception is None
        assert self.result.is_success is True
        assert self.storage.get("contexts.Shared")[-1] == "new_item"
        
    def _then_raises_type_mismatch_error(self):
        # 根据实际业务异常类型进行断言
        assert self.exception is not None
        assert "TypeMismatch" in type(self.exception).__name__
```

## 4. Vibe Coding 开发工作流

基于以上标准，日常开发与引入 AI Agent 的工作流如下：

1. **定义业务事实**：开发者在 `codegen.yaml` 中更新 `rules` 的自然语言描述。
2. **生成活文档**：运行 `codegen` 工具，工具将根据 YAML 全量刷新 `test_*.py`，生成不可变的、函数式组织的测试骨架。
3. **Agent 测试驱动 (TDD)**：
    * 运行 `pytest`。测试将因为抛出 `NotImplementedError` 报错退出，并精准提示哪个自然语言语义尚未实现。
    * Agent 捕捉到报错文本（如 `"未实现的 Given 语义..."`），自动前往 `bindings_*.py`。
    * Agent 在对应的 `match` 块中添加新的 `case` 分支，创建并实现对应的私有方法（`def _given_xxx(self):`）。
4. **验证与回归**：再次运行 `pytest`，绿灯通过。
