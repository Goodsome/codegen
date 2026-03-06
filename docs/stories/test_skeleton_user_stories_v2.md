# Codegen 测试骨架生成改进 — 用例重构用户故事 (V2)

> **背景**：当前 Codegen 已经经过了一轮迭代，采用了 AST 生成代码。但目前生成的 `cases_*.py` 依然采用了字典配合 `TypedDict` （即 `**kwargs` 模式）来作为测试用例的载体。  
> 
> 这种方式存在的缺陷：
> 1. 为了满足 `**kwargs` 参数 unpack，被迫生成了大量多余的 `XxxSetupArgs`、`XxxInputArgs` 等 `TypedDict`，代码显得冗长且臃肿。
> 2. `TypedDict` 只是提供 IDE 提示，开发者依然只能用原生字典 `{"id": "run-1", "current_phase": Phase.ARCHITECTURE}` 来构造对象。
> 3. 期望的测试驱动开发中，开发者应能够直接引用并构造领域模型本身（例如直接 [WorkflowRun(id="run-1", ...)](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/test_workflow_run.py#10-65)），这样能充分享受领域模型自身的校验逻辑与原生类型提示。
>
> **核心诉求**：**废弃 `**kwargs` 参数化模式**。在 cases 中直接传递构造好的领域模型对象（setup）、以及具体的行为入参（act），在 test 函数中直接定义具体参数名代替 `setup_args` 和 `method_input_args`。

---

## 核心用户故事：基于具体参数与领域原生的测试用例骨架

**作为** codegen 的使用者（开发者），  
**我希望** 测试文件能直接将领域模型和操作参数作为 fixture/parametrize 参数展开，而不再使用 `setup_args` / `method_input_args` 字典打包，  
**以便** 我在 `cases_*.py` 中可以通过直接实例化模型对象来编写测试数据，充分享受强类型与领域原生的直观体验。

### 当前现状分析：过于泛化的 kwargs 模式

目前的生成代码模式：
```python
# cases_workflow_run.py
class AdvancePhaseInputArgs(TypedDict):
    result: PhaseResult

class AdvancePhaseCase(NamedTuple):
    setup_args: WorkflowRunSetupArgs
    method_input_args: AdvancePhaseInputArgs
    expected: Any

# test_workflow_run.py 
# 参数全被打包在了 setup_args 和 method_input_args 两个大字典里
def test_advance_phase(self, target_class, setup_args, method_input_args, expected) -> None:
    instance = target_class(**setup_args)
    result = instance.advance_phase(**method_input_args)
```

这种模式有非常重的机械感，不够 pythonic，并且增加认知负担。

---

### 期望行为 1：Aggregate/Entity 行为测试重构

**[cases_workflow_run.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/cases_workflow_run.py) 期望格式**：

不再生成任何 `TypedDict`！直接引入领域原始类型，并在 `NamedTuple` 中把方法的真实入参展平。

```python
from typing import Any, Callable, NamedTuple
from agent_flow.orchestration.domain.enums import Phase, WorkflowStatus
from agent_flow.orchestration.domain.value_objects import PhaseResult
from agent_flow.orchestration.domain.aggregates.workflow_run import WorkflowRun

# 测试目标: advance_phase(self, result: PhaseResult) -> None
class AdvancePhaseCase(NamedTuple):
    # 🌟 1. setup: 直接要求传入一个现成的模型实例对象（或其他能提供模型实例的 fixture）
    # 或者如果觉得强制传实例会有状态污染风险，可以传一个能返回实例的 factory callable (即 Callable[[], WorkflowRun])。
    # 这里推荐直接传 `instance: WorkflowRun`，开发者直接实例化领域模型。
    instance: WorkflowRun
    
    # 🌟 2. method inputs: 直接展平为具体参数名称
    result: PhaseResult
    
    # 🌟 3. expected: 断言
    expected: Callable[[WorkflowRun], None]

TEST_CASES_ADVANCE_PHASE: list[AdvancePhaseCase] = [
    # 示例注释（由于 AST 会丢失纯注释，建议直接生成一条被注释掉的真实 Python 代码列表作为开发者参考，
    # 或者如果 AST 控制困难，直接留空列表，但通过精简后的 NamedTuple 强制了类型结构）。
]
```

**[test_workflow_run.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/test_workflow_run.py) 期望格式**：

测试函数的参数签名，应当与 `NamedTuple` 定义完全一致。不再存在 `**kwargs` 拆包！

```python
import pytest
from .cases_workflow_run import TEST_CASES_ADVANCE_PHASE

class TestWorkflowRun:

    # 🌟 注意参数列表已被展平，和 cases 中定义的 NamedTuple 的属性一一对应
    @pytest.mark.parametrize("instance, result, expected", TEST_CASES_ADVANCE_PHASE)
    def test_advance_phase(self, instance, result, expected) -> None:
        # 直接拿拿对象实例和明确的具体参数调用行为
        actual = instance.advance_phase(result=result)
        
        if callable(expected):
            expected(instance)  # 对象状态断言
        else:
            assert actual == expected
```

---

### 期望行为 2：Use Case / Domain Service 行为测试重构

同理，不再使用 `input_args: dict`。

**[cases_invoke_agent.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/execution/application/use_cases/cases_invoke_agent.py) 期望格式**：

```python
from typing import Any, Callable, NamedTuple
from agent_flow.execution.domain.value_objects import AgentConfig
from agent_flow.execution.application.use_cases.invoke_agent import InvokeAgentResult

# 测试目标: execute(self, prompt: str, config: AgentConfig) -> InvokeAgentResult
class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    
    # 🌟 直接展平该 Command/Query 的所有属性作为方法入参
    prompt: str
    config: AgentConfig
    
    expected: InvokeAgentResult

TEST_CASES_EXECUTE: list[ExecuteCase] = []
```

**[test_invoke_agent.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/execution/application/use_cases/test_invoke_agent.py) 期望格式**：

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from .cases_invoke_agent import TEST_CASES_EXECUTE

class TestInvokeAgent:

    @pytest.fixture
    def agent_gateway(self) -> None:
        return MagicMock()

    @pytest.fixture
    def invocation_repository(self) -> None:
        return MagicMock()

    @pytest.fixture
    def use_case(self, agent_gateway, invocation_repository) -> None:
        from agent_flow.execution.application.use_cases.invoke_agent import InvokeAgent
        return InvokeAgent(
            agent_gateway=agent_gateway, invocation_repository=invocation_repository
        )

    # 🌟 参数展平匹配 cases 定义
    @pytest.mark.parametrize("mocks_setup, prompt, config, expected", TEST_CASES_EXECUTE)
    def test_execute(self, use_case, agent_gateway, invocation_repository, mocks_setup, prompt, config, expected) -> None:
        mocks_setup(agent_gateway, invocation_repository)
        
        # 🌟 以显式 kwargs 形式调用具体参数
        result = use_case.execute(prompt=prompt, config=config)
        assert result == expected
```

---

### 验收标准

1. **废绝打包字典**：所有生成的 `cases_*.py` 中不应再出现为了模拟参数而生成的 `TypedDict`（如 [WorkflowRunSetupArgs](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/cases_workflow_run.py#9-16)）。
2. **入参展平到 NamedTuple**：用作 cases 的 `NamedTuple`（如 [AdvancePhaseCase](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/cases_workflow_run.py#22-26)），其属性应当明确罗列：
   - Aggregate 测试中：`instance`（具体的 Aggregate 类型）、以及该方法所需的所有参数（直接写类型，如 `result: PhaseResult`）。
   - Command/Query 测试中：`mocks_setup`、以及 Command/Query 字典展开后的所有独立参数名、`expected`（明确的预期返回类型）。
3. **显式传参**：`test_*.py` 文件中的测试方法签名，需将 parameters 展平（与上面的 `NamedTuple` 字段对应），并在测试内显式传参给对应的被测方法，例如 `use_case.execute(prompt=prompt, config=config)`。
4. **模型直接引用**：`cases_*.py` 必须引入 [codegen.yaml](file:///Users/xxxx/Projects/agent-flow/codegen.yaml) 中涉及到的真实的领域模型（Aggregate/Entity/ValueObject）类型，作为 `NamedTuple` 中属性的类型注解。
