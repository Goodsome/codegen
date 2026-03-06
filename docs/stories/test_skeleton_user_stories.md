# Codegen 测试骨架生成改进 — 用户故事

> **背景**：当前 `codegen build` 命令为 `agent-flow` 项目生成了测试骨架，采用
> `cases_*.py`（数据文件）+ `test_*.py`（驱动文件）的分层结构。  
> 开发者只需在 `cases_*.py` 中填写测试用例数据，即可让参数化测试自动运行。  
> 然而在分析现有骨架后，我们发现多处结构性缺陷，导致"只填 cases 即可测试"的目标**无法实现**。

---

## 问题汇总（当前现状）

```
tests/unit/
├── orchestration/
│   ├── domain/aggregates/
│   │   ├── cases_workflow_run.py          # ❌ 只有空列表，无结构说明
│   │   └── test_workflow_run.py           # ❌ 行为测试调用了构造器而非行为方法
│   └── application/use_cases/
│       ├── cases_start_workflow.py        # ❌ 只有空列表，无结构说明
│       ├── test_start_workflow.py         # ❌ UseCase() 未注入依赖
│       ├── cases_execute_phase.py
│       └── test_execute_phase.py         # ❌ 同上
├── execution/ ...                         # 同类问题
└── sop_management/ ...                    # 同类问题
```

---

## 用户故事 1 — cases 文件应生成带结构注释的类型化模板

**作为** codegen 的使用者（开发者），  
**我希望** 生成的 `cases_*.py` 文件中包含每条 case 应填写的字段注释和示例，  
**以便** 我无需阅读对应的实现源码，就能直接填写正确格式的测试数据。

### 当前现状

[cases_workflow_run.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/cases_workflow_run.py)：
```python
TEST_CASES_ADVANCE_PHASE: list = []
TEST_CASES_COMPLETE: list = []
TEST_CASES_FAIL: list = []
TEST_CASES_IS_FINAL_PHASE: list = []
```

### 期望行为

[cases_workflow_run.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/cases_workflow_run.py) 应生成带类型提示和注释的模板：

```python
from typing import Any

# 每条 case 格式: (setup_args: dict, method_input_args: dict, expected: Any)
# setup_args   — 用于构造被测聚合的初始化参数（对应 __init__ 签名）
# method_input_args — 传给 behavior 方法的参数
# expected    — 方法执行后的返回值（或断言对象状态的 callable）
#
# 示例:
# TEST_CASES_ADVANCE_PHASE = [
#     (
#         {"id": "run-1", "requirement": "...", "current_phase": Phase.ARCHITECTURE,
#          "status": WorkflowStatus.RUNNING, "phase_results": []},
#         {"result": PhaseResult(phase=Phase.ARCHITECTURE, status="done", artifacts=[])},
#         None,  # advance_phase 无返回值
#     ),
# ]
TEST_CASES_ADVANCE_PHASE: list[tuple[dict, dict, Any]] = []
TEST_CASES_COMPLETE: list[tuple[dict, dict, Any]] = []
TEST_CASES_FAIL: list[tuple[dict, dict, Any]] = []
TEST_CASES_IS_FINAL_PHASE: list[tuple[dict, dict, Any]] = []
```

### 验收标准

- [ ] `cases_*.py` 文件为每个行为 / 操作生成正确类型签名的变量（`list[tuple[dict, dict, Any]]`）
- [ ] 文件顶部包含参数含义的块注释
- [ ] 至少包含一条注释掉的示例数据，反映 [codegen.yaml](file:///Users/xxxx/Projects/agent-flow/codegen.yaml) 中真实的属性名和类型

---

## 用户故事 2 — 聚合行为测试应调用行为方法，而非重新构造对象

**作为** codegen 的使用者（开发者），  
**我希望** 针对聚合/值对象 **behavior** 的测试骨架能正确地先构造聚合实例、再调用对应的行为方法，  
**以便** 我只需填写 cases 数据就能真正测试领域行为逻辑，而无需修改 `test_*.py` 本身。

### 当前现状

[test_workflow_run.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/test_workflow_run.py)（所有行为测试均以相同错误模式生成）：

```python
@pytest.mark.parametrize("input_args,expected", TEST_CASES_ADVANCE_PHASE)
def test_advance_phase(self, target_class, input_args, expected) -> None:
    result = target_class(**input_args)   # ❌ 这里调用的是构造器，而非 advance_phase()
    assert result == expected
```

**问题分析**：[target_class(**input_args)](file:///Users/xxxx/Projects/agent-flow/tests/unit/sop_management/domain/aggregates/test_sop.py#7-12) 只是在实例化类，完全没有调用 [advance_phase](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/domain/aggregates/test_workflow_run.py#18-22) 方法，测试永远无法验证行为逻辑。

### 期望行为

行为测试应分为两步：**构造（setup）→ 执行行为（act）→ 断言**：

```python
@pytest.mark.parametrize("setup_args,method_input_args,expected", TEST_CASES_ADVANCE_PHASE)
def test_advance_phase(self, target_class, setup_args, method_input_args, expected) -> None:
    instance = target_class(**setup_args)          # 构造聚合实例
    result = instance.advance_phase(**method_input_args)  # 调用被测行为
    assert result == expected
```

对于改变状态的行为（返回 `None`），期望值可以是一个 callable（用于验证对象状态）：

```python
@pytest.mark.parametrize("setup_args,method_input_args,expected", TEST_CASES_COMPLETE)
def test_complete(self, target_class, setup_args, method_input_args, expected) -> None:
    instance = target_class(**setup_args)
    instance.complete(**method_input_args)
    if callable(expected):
        expected(instance)                # 通过回调验证聚合状态
    else:
        assert instance == expected
```

### 验收标准

- [ ] 聚合行为测试的参数签名统一为 [(setup_args, method_input_args, expected)](file:///Users/xxxx/Projects/agent-flow/tests/unit/sop_management/domain/services/test_sop_selector.py#7-12)
- [ ] 测试方法体先用 `setup_args` 构造实例，再用 `method_input_args` 调用对应方法
- [ ] `cases_*.py` 中对应的 case 格式与参数签名一致（三元组）
- [ ] 对于 `output.type == None` 的行为，骨架在断言处生成注释提示（"验证对象状态而非返回值"）

---

## 用户故事 3 — 用例（Use Case）测试应通过 Mock 注入依赖

**作为** codegen 的使用者（开发者），  
**我希望** 用例测试骨架能自动识别用例的 `dependencies`（来自 [codegen.yaml](file:///Users/xxxx/Projects/agent-flow/codegen.yaml)），并用 `unittest.mock.MagicMock` 生成 fixture，  
**以便** 我可以在 cases 文件中指定 mock 的行为，而无需修改 `test_*.py`。

### 当前现状

[test_start_workflow.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/test_start_workflow.py)：
```python
@pytest.fixture
def use_case(self) -> None:
    from agent_flow.orchestration.application.use_cases.start_workflow import StartWorkflow
    return StartWorkflow()    # ❌ 无参数构造，无 mock 依赖注入
```

**问题分析**：[StartWorkflow](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/test_start_workflow.py#5-19) 依赖 `WorkflowRunRepository`，[ExecutePhase](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/test_execute_phase.py#5-19) 依赖 `WorkflowRunRepository + SopSelector + AgentGateway`。直接 `UseCase()` 会在运行时报缺少参数错误，测试根本无法运行。

### 期望行为（以 [StartWorkflow](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/test_start_workflow.py#5-19) 为例）

**[test_start_workflow.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/test_start_workflow.py)**：

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from .cases_start_workflow import TEST_CASES_EXECUTE


class TestStartWorkflow:

    @pytest.fixture
    def workflow_run_repository(self):
        return MagicMock()          # 自动生成：对应 dependency name

    @pytest.fixture
    def use_case(self, workflow_run_repository):
        from agent_flow.orchestration.application.use_cases.start_workflow import StartWorkflow
        return StartWorkflow(workflow_run_repository=workflow_run_repository)

    @pytest.mark.parametrize("mocks_setup,input_args,expected", TEST_CASES_EXECUTE)
    def test_execute(self, use_case, workflow_run_repository, mocks_setup, input_args, expected) -> None:
        mocks_setup(workflow_run_repository)    # 由 case 配置 mock 行为
        result = use_case.execute(**input_args)
        assert result == expected
```

**[cases_start_workflow.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/cases_start_workflow.py)**：

```python
from typing import Any, Callable
from unittest.mock import MagicMock

# 每条 case 格式: (mocks_setup: Callable, input_args: dict, expected: Any)
# mocks_setup  — 接收各依赖 mock 对象，配置其返回值和断言
# input_args   — 传给 use_case.execute() 的参数（对应 Command/Query 属性）
# expected     — execute() 的返回值（对应 Result 类型）
#
# 示例:
# def _mock_start_workflow(workflow_run_repository):
#     workflow_run_repository.save.return_value = None
#
# TEST_CASES_EXECUTE = [
#     (
#         _mock_start_workflow,
#         {"command": StartWorkflowCommand(requirement="实现登录功能")},
#         StartWorkflowResult(workflow_run_id="some-uuid"),
#     ),
# ]
TEST_CASES_EXECUTE: list[tuple[Callable, dict, Any]] = []
```

### 验收标准

- [ ] `test_*.py` 为每个 `dependency` 自动生成独立的 `@pytest.fixture`（使用 `MagicMock`）
- [ ] [use_case](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/test_start_workflow.py#7-14) fixture 将所有 mock dependency 以关键字参数注入构造器
- [ ] [test_execute](file:///Users/xxxx/Projects/agent-flow/tests/unit/orchestration/application/use_cases/test_advance_phase.py#15-19) 的参数签名为 [(mocks_setup, input_args, expected)](file:///Users/xxxx/Projects/agent-flow/tests/unit/sop_management/domain/services/test_sop_selector.py#7-12)，并在方法体中调用 `mocks_setup(*deps)`
- [ ] `cases_*.py` 的 case 格式注释反映三元组结构，并提供示例
- [ ] 支持异步用例（`async def execute`）时自动使用 `AsyncMock` 和 `pytest.mark.asyncio`

---

## 用户故事 4 — Domain Service 测试应同样注入 Mock 依赖

**作为** codegen 的使用者（开发者），  
**我希望** 领域服务（Domain Service）的测试骨架与用例测试一样，能正确 mock 其声明的 `dependencies`，  
**以便** 服务层测试与用例测试遵循一致的结构规范。

### 当前现状

[test_sop_selector.py](file:///Users/xxxx/Projects/agent-flow/tests/unit/sop_management/domain/services/test_sop_selector.py)：
```python
@pytest.fixture
def service(self) -> None:
    from agent_flow.sop_management.domain.services.sop_selector import SopSelector
    return SopSelector()    # ❌ SopSelector 依赖 SopRepository，无法空构造
```

### 期望行为

```python
@pytest.fixture
def sop_repository(self):
    return MagicMock()

@pytest.fixture
def service(self, sop_repository):
    from agent_flow.sop_management.domain.services.sop_selector import SopSelector
    return SopSelector(sop_repository=sop_repository)

@pytest.mark.parametrize("mocks_setup,input_args,expected", TEST_CASES_SELECT_FOR_PHASE)
def test_select_for_phase(self, service, sop_repository, mocks_setup, input_args, expected) -> None:
    mocks_setup(sop_repository)
    result = service.select_for_phase(**input_args)
    assert result == expected
```

### 验收标准

- [ ] Domain Service 骨架生成与 Use Case 骨架完全相同的依赖 mock fixture 模式
- [ ] `cases_*.py` 格式与 Use Case cases 文件保持一致（三元组 + 注释）

---

## 用户故事 5 — Infrastructure 实现类应生成单元测试骨架

**作为** codegen 的使用者（开发者），  
**我希望** [codegen.yaml](file:///Users/xxxx/Projects/agent-flow/codegen.yaml) 中 `infrastructure.implementations` 下定义的每个实现类，都能在 `tests/unit/<context>/infrastructure/` 目录下生成对应的 `cases_*.py` + `test_*.py` 骨架，  
**以便** 我可以通过填写 cases 数据来验证基础设施适配器的行为，而无需手动创建测试文件。

### 当前现状

[codegen.yaml](file:///Users/xxxx/Projects/agent-flow/codegen.yaml) 中定义了以下 infrastructure 实现类，但 `tests/unit/` 下**完全没有对应的测试目录和文件**：

| 上下文 | 实现类 | 实现接口 | 测试文件 |
|-------|--------|---------|--------|
| Execution | `ClaudeSdkGateway` | `AgentGateway` | ❌ 不存在 |
| Execution | `GeminiCliGateway` | `AgentGateway` | ❌ 不存在 |
| SopManagement | `YamlSopRepository` | `SopRepository` | ❌ 不存在 |

```
tests/unit/
├── execution/
│   ├── application/   ✅ 已生成
│   ├── domain/        ✅ 已生成
│   └── infrastructure/ ❌ 完全缺失
└── sop_management/
    ├── application/   ✅ 已生成
    ├── domain/        ✅ 已生成
    └── infrastructure/ ❌ 完全缺失
```

### 期望行为

应生成如下目录结构和文件：

```
tests/unit/
├── execution/infrastructure/
│   ├── __init__.py
│   ├── cases_claude_sdk_gateway.py
│   ├── test_claude_sdk_gateway.py
│   ├── cases_gemini_cli_gateway.py
│   └── test_gemini_cli_gateway.py
└── sop_management/infrastructure/
    ├── __init__.py
    ├── cases_yaml_sop_repository.py
    └── test_yaml_sop_repository.py
```

**`test_claude_sdk_gateway.py`** 示例：

```python
import pytest
from unittest.mock import MagicMock
from .cases_claude_sdk_gateway import TEST_CASES_INVOKE


class TestClaudeSdkGateway:

    @pytest.fixture
    def gateway(self):
        from agent_flow.execution.infrastructure.claude_sdk_gateway import ClaudeSdkGateway
        return ClaudeSdkGateway()   # 无依赖端口，直接构造

    @pytest.mark.parametrize("mocks_setup,input_args,expected", TEST_CASES_INVOKE)
    def test_invoke(self, gateway, mocks_setup, input_args, expected) -> None:
        mocks_setup()               # 配置外部依赖（如 patch Claude SDK）
        result = gateway.invoke(**input_args)
        assert result == expected
```

**`cases_claude_sdk_gateway.py`** 示例：

```python
from typing import Any, Callable

# 每条 case 格式: (mocks_setup: Callable, input_args: dict, expected: Any)
# mocks_setup  — 使用 unittest.mock.patch 模拟外部 SDK / 子进程调用
# input_args   — 传给接口方法的参数（对应 Port operation 的 inputs）
# expected     — 方法返回值（对应 Port operation 的 output 类型）
#
# 示例:
# from unittest.mock import patch
# def _mock_invoke():
#     # patch Claude SDK 客户端
#     pass
#
# TEST_CASES_INVOKE = [
#     (
#         _mock_invoke,
#         {"prompt": "实现登录功能", "config": AgentConfig(provider=AgentProvider.CLAUDE_SDK, allowed_tools=[])},
#         ExecutionResult(output="...", status="completed", artifacts=[]),
#     ),
# ]
TEST_CASES_INVOKE: list[tuple[Callable, dict, Any]] = []
```

### 验收标准

- [ ] 为每个 `infrastructure.implementations` 条目在 `tests/unit/<context>/infrastructure/` 下生成 `test_*.py` 和 `cases_*.py`
- [ ] 测试类名为 `Test<ImplementationName>`（如 `TestClaudeSdkGateway`）
- [ ] fixture 名称为 snake_case 的实现类名（如 `gateway` 或 `yaml_sop_repository`）
- [ ] 为实现类所实现的 Port 的每个 `operation` 生成对应的 `test_<operation_name>` 方法
- [ ] `cases_*.py` 中为每个 operation 生成对应的 `TEST_CASES_<OPERATION_NAME>` 变量，格式与 US-3 一致（三元组 + 注释）
- [ ] 若实现类无显式依赖端口（如 `ClaudeSdkGateway` 不依赖其他 Port），则 fixture 直接构造，不生成额外 mock fixture

---

## 附录：受影响文件一览

| 文件 | 问题类型 | 优先级 |
|------|---------|-------|
| `tests/unit/orchestration/domain/aggregates/test_workflow_run.py` | US-2：行为调用错误 | P0 |
| `tests/unit/orchestration/domain/aggregates/cases_workflow_run.py` | US-1：缺结构说明 | P0 |
| `tests/unit/orchestration/application/use_cases/test_start_workflow.py` | US-3：无依赖注入 | P0 |
| `tests/unit/orchestration/application/use_cases/cases_start_workflow.py` | US-1：缺结构说明 | P0 |
| `tests/unit/orchestration/application/use_cases/test_advance_phase.py` | US-3：无依赖注入 | P0 |
| `tests/unit/orchestration/application/use_cases/cases_advance_phase.py` | US-1：缺结构说明 | P0 |
| `tests/unit/orchestration/application/use_cases/test_execute_phase.py` | US-3：无依赖注入（3个依赖）| P0 |
| `tests/unit/orchestration/application/use_cases/cases_execute_phase.py` | US-1：缺结构说明 | P0 |
| `tests/unit/orchestration/application/use_cases/test_get_workflow_status.py` | US-3：无依赖注入 | P0 |
| `tests/unit/execution/domain/aggregates/test_agent_invocation.py` | US-2：行为调用错误 | P0 |
| `tests/unit/execution/domain/aggregates/cases_agent_invocation.py` | US-1：缺结构说明 | P0 |
| `tests/unit/execution/application/use_cases/test_invoke_agent.py` | US-3：无依赖注入（2个依赖）| P0 |
| `tests/unit/sop_management/domain/aggregates/test_sop.py` | US-2：行为调用错误 | P0 |
| `tests/unit/sop_management/domain/services/test_sop_selector.py` | US-4：Service无依赖注入 | P0 |
| `tests/unit/execution/infrastructure/` | US-5：目录完全缺失 | P0 |
| `tests/unit/sop_management/infrastructure/` | US-5：目录完全缺失 | P0 |
