# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- **Install dependencies**: `uv sync` or `pip install -e ".[dev]"` (Python 3.13+, uses `uv.lock`)
- **Lint code**: `ruff check .`
- **Run tests**: `uv run pytest`
- **Run a single test**: `pytest tests/path/to/test_file.py::test_function_name`

## Project Vision

用确定性的静态工具，为不确定性的 LLM 划定不可逾越的“脚手架”和“护栏”。

## Project Architecture & Structure
Codegen is a CLI tool that generates Domain-Driven Design (DDD) boilerplate code in Python from a single blueprint file (`codegen.yaml`).

- `codegen.yaml`: The central blueprint defining the domain models, bounded contexts, aggregates, entities, value objects, ports, and enums. It strongly uses a JSON schema (`codegen.schema.json`) for validation.
- `src/codegen/entrypoints/`: Contains entry points for the application - `cli` (using Typer) and `mcp` interfaces.
- `src/codegen/bootstrap.py`: Main dependency injection container wiring all components.
- `src/codegen/domain_definition/`: Contains the parsers and Pydantic models for representing the blueprint defined in `codegen.yaml`.
- `src/codegen/python_gen/`: Contains the logic and AST translators for generating the actual Python code from the domain definition.
- **Dependency Injection**: The project uses `dependency-injector` for wiring up components.
- **String Case Conversion**: Extensive use of `case-converter` is made for handling naming conventions (PascalCase, snake_case, camelCase) via types like `NamingString`, `SnakeString`, and `PascalString` defined in the exact blueprint.
