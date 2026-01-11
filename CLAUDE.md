# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Codegen** is a DDD (Domain-Driven Design) Project Scaffolding Tool. It reads a `codegen.yaml` configuration file describing a DDD project structure and generates Python code. It can also reverse-engineer existing Python packages back into a `codegen.yaml` blueprint.

## Commands

```bash
# Run tests
.venv\Scripts\python.exe -m pytest

# Run single test file
.venv\Scripts\python.exe -m pytest tests/test_blueprint.py

# Run single test function
.venv\Scripts\python.exe -m pytest tests/python_gen/domain/value_objects/test_enum_spec.py::test_enum_spec_create

# Lint with ruff
.venv\Scripts\python.exe -m ruff check src/

# Format with black
.venv\Scripts\python.exe -m black src/

# Type check with basedpyright
.venv\Scripts\python.exe -m basedpyright src/
```

CLI commands:
```bash
codegen              # Show help
codegen generate     # Generate code from blueprint
codegen generate-blueprint  # Reverse engineer Python package to YAML
```

## Architecture

The project uses **clean architecture** with four bounded contexts:

- **`domain_definition/`** - The "what": meta-model describing DDD structures (Blueprint, BoundedContext, Aggregate, etc.)
- **`python_gen/`** - The "how": Python code generation specifics (ClassSpec, ModuleSpec, PackageSpec, AST parsing, Jinja templates)
- **`orchestration/`** - The "bridge": mapping between meta-model and Python specs (DomainMapper, ContextMapper, etc.)
- **`shared/`** - Shared utilities (Entity, ValueObject, AggregateRoot base classes, NamingString)

## Key Patterns

### Mapper Pattern
Bidirectional mapping between meta-model and Python specs:
- `DomainMapper`, `ContextMapper`, `AggregateMapper`, `PortMapper`, etc.
- All support `to_package_spec()` and reverse `to_*()` methods

### Specification Objects
All domain definitions use Pydantic `BaseModel` subclasses with `extra="forbid"` for strict validation.

### Naming Utilities (`NamingString`)
Enhanced string types with case conversion at `src/codegen/shared/domain/value_objects/naming_string.py`:
- `PascalString` → PascalCase
- `SnakeString` → snake_case
- `MacroString` → MACRO_CASE
- Methods: `to_pascal()`, `to_snake()`, `to_kebab()`, `to_camel()`, `to_macro()`

## Dependency Injection

Uses `dependency-injector` library. Container is configured in `src/codegen/bootstrap.py`.

## File Organization

- `codegen.yaml` - Main DDD project configuration
- `codegen.schema.json` - JSON Schema for blueprint validation
- `src/codegen/python_gen/templates/` - Jinja2 templates for code generation
- `tests/` - Test files mirror source directory structure
- `conftest.py` - Pytest fixtures (`project_root`, `default_container`, `local_blueprint`)
