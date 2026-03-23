# Issue Tracking

> Last updated: 2026-03-19

---

## MCP Tool Issues

### T1: Array append syntax not supported
- **Problem**: `contexts[-]` and `contexts[2]` (out of bounds) both fail. Must use `append: true` parameter.
- **Workaround**: Always specify `append: true` when appending to arrays.
- **Suggestion**: Support `[-]` syntax for intuitive array appending.

### T2: JSON string incorrectly written
- **Problem**: When adding ports/components, the tool writes JSON objects as raw strings into YAML, corrupting the format.
- **Workaround**: Manually fix the YAML after the operation.
- **Suggestion**: Ensure `set` operation correctly parses nested objects.

### T3: `default` field only accepts strings
- **Problem**: `ConfigFieldSpec.default` field only accepts string type. Integer values must be converted to strings (e.g., `'10'`).
- **Workaround**: Pass numeric defaults as strings.

### T4: `output_type: None` generates incorrect code
- **Problem**: No validation on `output_type: None`, resulting in malformed generated code.
- **Suggestion**: Validate output_type before code generation.

### T5: Cannot operate when validation errors exist
- **Problem**: When validation errors exist, delete/fix operations are blocked, making tool-assisted recovery impossible.
- **Suggestion**: Allow delete/modify operations even with validation errors.

### T6: Bulk node build not supported [2026-03-22]
- **Problem**: Using `codegen build --node <name>` requires multiple calls when updating multiple nodes (e.g., 11 Spec types = 11 calls).
- **Suggestion**: Support batch node building via:
  - Comma-separated list: `--nodes AggregateSpec,EntitySpec,ValueObjectSpec`
  - Glob pattern: `--pattern "*Spec"`
  - Config file: `--from-file update_specs.json`

### T7: Path resolution error messages lack hints [2026-03-22]
- **Problem**: When `mcp__codegen__set` fails with "Path not found", error message doesn't suggest available paths.
- **Suggestion**: Include available path hints in error message:
  ```
  Path not found: "contexts.DomainDefinition.domain.value_objects.TypeDefinition"
  Hint: Available value_objects: UseCaseSpec, ApplicationSpec, ... (top 5-10)
  Did you mean: "contexts.DomainDefinition.domain.value_objects.UseCaseSpec"?
  ```

### T8: Set operation lacks post-write validation [2026-03-22]
- **Problem**: Tool returns success but data may be incorrectly written; requires manual verification via `get`.
- **Suggestion**:
  1. Auto-validate after `set` and return result summary
  2. Add dry-run mode: `codegen set --dry-run contexts.xxx value`

---

## Code Generation Issues (2026-03-19)

### ~~G1: CLI command names with spaces break `__init__.py` imports~~ [RESOLVED]
- **Status**: Resolved on 2026-03-19
- **Resolution**: Added `_sanitize_identifier()` method to `InterfaceMapper` that converts spaces and hyphens to underscores for CLI command names, MCP tool names, and their imports.
- **Commit**: (pending)
- **Tests**: `tests/unit/orchestration/domain/services/test_interface_mapper_cli.py`

### G2: Missing `from __future__ import annotations` for self-referencing types [BLOCKER]
- **Severity**: High
- **Problem**: Methods returning `Self` type cause `NameError: name 'ClassName' is not defined`.
- **Error**:
  ```python
  class IssueId(ValueObject):
      def create(self) -> IssueId: ...  # NameError!
  ```
- **Affected**: All value objects, entities, aggregate roots
- **Fix**: Add `from __future__ import annotations` to all generated class files.

### G3: External types not auto-imported [BLOCKER]
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

### G4: `--node` parameter behavior unexpected [BLOCKER]
- **Severity**: High
- **Problem**: Using `--node` to update a single component replaces the entire array instead of matching element.
- **Example**:
  ```yaml
  # Before
  use_cases:
  - name: CreateIssue
  - name: UpdateIssueStatus
  - name: ListIssues

  # After mcp__codegen__set --node CreateIssue
  use_cases:
  - name: CreateIssue  # Other two lost!
  ```
- **Fix**: `--node` should locate matching element and update in-place.

---

## Tool Enhancement Suggestions

| Suggestion | Expected Behavior | Value |
|------------|-------------------|-------|
| Support `[-]` append syntax | No need to specify `append: true` each time | Reduces cognitive load, consistent with common YAML operations |
| Bulk write interface | `mcp__codegen__set_bulk` supports writing multiple sibling components | Reduces network round-trips, improves efficiency |
| JSON object parsing | Ensure `set` correctly parses nested objects | Prevents format corruption |
| Operate despite validation errors | Allow delete/fix when validation errors exist | Enables tool-assisted recovery |

---

## Summary Matrix

| Issue | Severity | Status | Notes |
|-------|----------|--------|-------|
| T1: Array append syntax | Medium | Open | Use `append: true` |
| T2: JSON string corruption | Medium | Open | Manual YAML fix |
| T3: Default field strings only | Low | Open | Pass as string |
| T4: output_type: None validation | Medium | Open | Validate before build |
| T5: Blocked by validation errors | Medium | Open | Manual intervention |
| T6: Bulk node build | Low | Open | Batch build support |
| T7: Path error hints | Low | Open | Enhance error messages |
| T8: Post-write validation | Low | Open | Auto-validate set operations |
| ~~G1: CLI identifier transform~~ | ~~High~~ | **Resolved** | Added `_sanitize_identifier()` |
| G2: Missing future annotations | High | Open | Manual import addition |
| G3: External type imports | High | Open | Manual placeholder imports |
| G4: --node behavior | High | Open | Avoid `--node` |