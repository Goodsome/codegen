# User Story: E2E Test Suite for Codegen

## Context
Codegen 项目目前缺乏端到端 (E2E) 测试。现有的测试主要集中在单元层面 (Unit Tests)。
为了确保从 "读取 Blueprint" 到 "生成可运行代码" 的完整链路的稳定性，我们需要引入 E2E 测试。

## Goals
1. **验证完整链路**：确保 `codegen.yaml` 能被正确解析，并生成符合预期的文件结构。
2. **验证生成代码的有效性**：生成的 Python 代码应当没有语法错误，且可以被解释器加载。
3. **防止回归**：在重构架构（如引入 Bootstrap 和 Interfaces 层）时，确保核心生成逻辑不被破坏。

## Scenarios

### Scenario 1: Standard DDD Project Generation
* **Given**: 一个包含完整 DDD 元素 (Context, Aggregate, Reference, Command, Event) 的 `codegen.yaml`。
* **When**: 运行 `codegen build` 命令。
* **Then**:
    * 目标目录下生成了完整的项目结构。
    * 包含 `domain`, `application`, `infrastructure`, `interfaces`, `bootstrap` 等目录。
    * 生成的 Python 文件符合语法规范 (可被 `ast.parse` 或 `python -m compileall` 验证)。

### Scenario 2: CLI Interface Verification
* **Given**: `codegen` 环境已准备就绪。
* **When**: 执行 `codegen build --config-file ... --work-dir ...`。
* **Then**: 命令返回成功状态码 (0)，且指定目录下存在生成的文件。

### Scenario 3: Syntax Validity Check
* **Given**: 生成的代码。
* **When**: 运行语法检查工具 (如 `python -m compileall` 或 `ast.parse`)。
* **Then**: 不应报告任何 SyntaxError。

## Implementation Suggestion
* 使用 `pytest` 结合 `tmp_path` fixture 创建临时工作目录。
* 在 `tests/e2e/fixtures/` 下维护真实的 `codegen.yaml` 样例。
* 优先使用 Python API 调用 (`codegen.main` 或类似入口) 进行测试，以提高速度和调试便利性；必要时辅以 `subprocess` 测试 CLI 入口。
