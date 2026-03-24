# Issue Tracking

> Last updated: 2026-03-24

本文档用于跟踪 Codegen 项目中的问题、缺陷和改进建议。

## 如何添加新 Issue

1. 新 Issue 使用 uuid 作为编号
2. 在 Issue 列简述问题
3. 在 Notes 列填相关描述
4. 填写详细信息，比如 BUG 复现场景。

## 如何清理已处理的 Issue

当某个 Issue 被修复后，从表格和下方详细信息中同步删除该条目。

---

| # | Issue | Severity | Status | Notes |
|-------|-------|----------|--------|-------|
| 6 | Bulk node build | Low | Open | Batch build support |
| 10 | External type imports | High | Open | Manual placeholder imports |

---

## Issue 6: Bulk node build not supported
- **Problem**: Using `codegen build --node <name>` requires multiple calls when updating multiple nodes (e.g., 11 Spec types = 11 calls).
- **Suggestion**: Support batch node building via:
  - Comma-separated list: `--nodes AggregateSpec,EntitySpec,ValueObjectSpec`
  - Glob pattern: `--pattern "*Spec"`
  - Config file: `--from-file update_specs.json`

## Issue 10: External types not auto-imported
- **Severity**: High
- **Problem**: External types defined in blueprint (e.g., `Session`, `Connection`, `DomainEvent`) are not auto-imported, causing `NameError`.
- **Affected Files**:
  - `infrastructure/repositories/*.py` - missing `Session` import
  - `infrastructure/adapters/*.py` - missing `Connection` import
  - `domain/ports/*.py` - missing `DomainEvent` type import
- **Suggested Fix**:
  ```yaml
  implementations:
  - name: SqlAlchemyIssueRepository
    implements: IssueRepository
    technology: sql
    external_imports:
    - from: sqlalchemy.orm
      import: Session
  ```
