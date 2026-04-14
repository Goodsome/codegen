---
name: 0001 确立 codegen.yaml 为唯一真实数据源 (SSOT)
status: accepted
date: 2026-04-14
---

# ADR-0001: 确立 codegen.yaml 为唯一真实数据源 (SSOT)

## 背景
早期在 Markdown 设计文档和 YAML 蓝图中存在大量冗余的字段与规则定义，导致 AI Agent 和人类开发者陷入“双写”状态不同步的灾难。LLM 经常会在文档中查找字段定义，而忽略了 YAML 中的实际配置，产生大量幻觉。

## 决策
1. 全面缩减 Markdown 文档，将其转型为仅记录高维决策与算法的“战略图纸”；
2. 将实体、值对象、领域服务及 BDD 规则 (rules) 全部下沉到 `codegen.yaml` 中；
3. 任何业务逻辑相关的结构化字段必须只存在于 YAML 中，禁止在 Markdown 中重复定义。

## 影响
1. 极大降低了 LLM 的 Context Token 消耗，提高了开发的确定性；
2. 彻底消灭了双写导致的状态不一致问题；
3. YAML 成为所有工具链的唯一输入源，简化了系统设计。
