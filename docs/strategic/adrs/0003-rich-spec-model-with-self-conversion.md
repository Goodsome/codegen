---
name: 0003 采用充血模型赋予 Spec 自我转换能力
status: accepted
date: 2026-04-14
---

# ADR-0003: 采用充血模型赋予 Spec 自我转换能力

## 背景
在早期设计中，将 YAML 蓝图转换为具体 Python 代码树的知识泄露在了 Orchestration 编排层，导致耦合严重，修改代码生成逻辑需要同时修改多个上下文的代码。

## 决策
1. 将 DomainDefinition 确立为 PythonGen 的“顺从者 (Conformist)”；
2. 为所有 Spec（值对象）赋予 `to_module_spec()` 等行为方法，使其能够自我转换为下游代码生成器需要的模型；
3. 转换逻辑全部沉淀在 DomainDefinition 上下文内部，Orchestration 和 PythonGen 不需要了解转换细节。

## 影响
1. 消除了上下文之间的耦合，代码生成逻辑的修改只需要调整 DomainDefinition 上下文；
2. 提高了代码的内聚性，转换逻辑与模型定义放在一起，更容易维护；
3. PythonGen 可以专注于代码渲染逻辑，不需要关心领域模型的细节。
