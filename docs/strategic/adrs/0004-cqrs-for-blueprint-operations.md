---
name: 0004 基于路径操作的 CQRS 模式
status: accepted
date: 2026-04-14
---

# ADR-0004: 基于路径操作的 CQRS 模式

## 背景
针对庞大 YAML 蓝图的细粒度操作（如 CLI/MCP 下发的 get, set, rm 命令）需要保证内存安全和单向数据流，避免并发修改导致的数据不一致。

## 决策
在应用层实施命令与查询分离 (CQRS)：
1. **命令 (Command)**: 使用 `BlueprintPathOperations` 进行不可变更新（Pydantic `model_copy`），完成 `load -> modify -> save` 的完整事务单元；
2. **查询 (Query)**: 直接通过 `BlueprintPathResolver` 领域服务解析路径取值，不触发持久化操作。

## 影响
1. 实现了读写分离，提高了系统的并发性能；
2. 不可变更新保证了数据的一致性，避免了副作用；
3. 命令和查询职责清晰，更容易维护和测试。
