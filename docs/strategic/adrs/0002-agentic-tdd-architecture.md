---
name: 0002 BDD 测试驱动架构 (Agentic TDD)
status: accepted
date: 2026-04-14
---

# ADR-0002: BDD 测试驱动架构 (Agentic TDD)

## 背景
如何让 AI 稳定地实现复杂的底层业务逻辑，避免 LLM 自由发挥产生不符合预期的代码。

## 决策
1. 在 YAML 中引入 `given/when/then` 的 rules 节点，定义 BDD 风格的测试规则；
2. Codegen 工具直接生成 `test_*.py` 和带有 `NotImplementedError` + `match-case` 路由的 `bindings_*.py`；
3. 利用测试报错驱动 Agent 进行填空式开发，确保所有实现都满足预定义的测试规则。

## 影响
1. 实现了“需求 -> 测试 -> 实现”的确定性开发流程；
2. 大幅降低了 LLM 实现代码的错误率；
3. 测试用例成为业务需求的可执行描述，避免了需求与实现的脱节。
