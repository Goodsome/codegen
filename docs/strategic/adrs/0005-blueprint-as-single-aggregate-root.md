---
name: 0005 确立 Blueprint 为全局单一聚合根
status: accepted
date: 2026-04-14
---

# ADR-0005: 确立 Blueprint 为全局单一聚合根并废弃泛型路径更新

## 背景
之前系统倾向于将 Blueprint 视为嵌套字典，并使用泛型的 JSON Path 机制（`set_value`）进行深层更新。这不仅导致 Pydantic 的深层数据校验经常被绕过（产生脏数据），也使得业务意图（如"为实体添加属性"）在日志和工具调用中丢失，极易引发大语言模型产生幻觉。

## 决策
1. 正式确立 `Blueprint` 为 DomainDefinition 上下文中的唯一聚合根；
2. 废弃基于路径的泛型数据外科手术，转向"明确意图的命令 (Intent-Revealing Commands)"，如 `AddAttributeCommand`, `AddEntityCommand`；
3. 所有针对深层实体（如 `EntitySpec`）和值对象（如 `Attribute`）的增删改，必须作为 Command 统一发送给 `Blueprint` 聚合根，由其内部通过 Name/ID 寻址并完成状态变更，最后统一触发一致性校验。

## 影响
1. 后续必须重构现有的 `mcp__codegen__set` 工具，逐步拆分为强类型的具名工具；
2. `BlueprintPathOperations` 将降级为仅供只读查询或非核心补漏使用的工具；
3. 彻底消除了脏数据的产生，所有修改都经过完整的业务规则校验；
4. 工具调用的业务意图明确，大幅降低了 LLM 的幻觉概率。
