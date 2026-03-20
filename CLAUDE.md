# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- **Install dependencies**: `uv sync` or `pip install -e ".[dev]"` (The project uses Python 3.13+ and has a `pyproject.toml` and `uv.lock`)
- **Format code**: `black .`
- **Lint code**: `ruff check .`
- **Run tests**: `pytest`
- **Run a single test**: `pytest tests/path/to/test_file.py::test_function_name`
- **Generate code**: `codegen generate` (uses `codegen.yaml`)
- **Run the CLI**: `codegen [command]` (e.g., `codegen add context Billing`)
- **Run MCP Server**: `codegen-mcp`

## Project Vision

用确定性的静态工具，为不确定性的 LLM 划定不可逾越的“脚手架”和“护栏”。

## Project Architecture & Structure
Codegen is a CLI tool that generates Domain-Driven Design (DDD) boilerplate code in Python from a single blueprint file (`codegen.yaml`).

- `codegen.yaml`: The central blueprint defining the domain models, bounded contexts, aggregates, entities, value objects, ports, and enums. It strongly uses a JSON schema (`codegen.schema.json`) for validation.
- `src/codegen/entrypoints/`: Contains the entry points for the application, specifically the `cli` (using Typer) and `mcp` interfaces.
- `src/codegen/domain_definition/`: Contains the parsers and Pydantic models for representing the blueprint defined in `codegen.yaml`.
- `src/codegen/python_gen/`: Contains the logic and AST translators for generating the actual Python code from the domain definition.
- **Dependency Injection**: The project uses `dependency-injector` for wiring up components.
- **String Case Conversion**: Extensive use of `case-converter` is made for handling naming conventions (PascalCase, snake_case, camelCase) via types like `NamingString`, `SnakeString`, and `PascalString` defined in the exact blueprint.

## Special Rules and Context
- **Context-Dependent Source of Truth**:
  - **For the `DomainDefinition` context (Core Models)**: The Python source code (in `src/codegen/domain_definition/`) is the absolute source of truth. When modifying or adding new domain component types or blueprint structures, you must modify the Python Pydantic models first. The generator cannot bootstrap its own domain models. After updating the Python models, run `codegen reverse` to update `codegen.yaml` and `codegen schema` to update `codegen.schema.json`.
  - **For other contexts / normal usage**: The `codegen.yaml` file is the absolute source of truth. Changes to those domain architectures should be reflected in the YAML first (or managed via `codegen add/update/delete` commands) to generate the corresponding code.
- **Naming Conventions**: Different parts of the code require specific casing. Pay attention to how `case-converter` or the custom string types (e.g., `NamingString`) are used to transform names between string representations.
