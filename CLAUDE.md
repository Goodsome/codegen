# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- **Install dependencies**: `uv sync` or `pip install -e ".[dev]"` (Python 3.13+, uses `uv.lock`)
- **Format code**: `black .`
- **Lint code**: `ruff check .`
- **Run tests**: `uv run pytest`
- **Run a single test**: `pytest tests/path/to/test_file.py::test_function_name`
- **Build code**: `codegen build` (compiles `codegen.yaml` into Python code)
- **Reverse engineer**: `codegen reverse` (updates `codegen.yaml` from Python code)
- **Output schema**: `codegen schema` (outputs JSON schema for the blueprint)
- **Initialize blueprint**: `codegen init` (creates a new `codegen.yaml`)
- **View blueprint**: `codegen tree` (displays blueprint as visual tree)
- **Query blueprint**: `codegen get <path>` (e.g., `codegen get contexts.sales`)
- **Update blueprint**: `codegen set <path> <value>` or `codegen rm <path>`
- **Run MCP Server**: `codegen mcp`

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

## Bounded Contexts & Design Documents

The project uses DDD with 3 bounded contexts, each with design documents in `docs/<context>/`:

### 1. DomainDefinition (领域定义)
**Core Responsibility**: Manages `codegen.yaml` blueprint as the single source of truth for code generation.

**Key Concepts**:
- `Blueprint` (根聚合): Root aggregate containing all bounded contexts
- `BoundedContext` (子聚合): Contains DomainSpec, ApplicationSpec, InfrastructureSpec, InterfaceSpec
- All Spec types (EntitySpec, ValueObjectSpec, AggregateSpec, PortSpec, etc.) are immutable value objects
- Uses `BlueprintStorage` port for YAML persistence

**Design Doc Summary**:
- *ddd-strategic*: Blueprint as single source of truth; OHS pattern for downstream contexts
- *ddd-tactical*: Aggregates (Blueprint/BoundedContext), Value Objects (all Spec types), Domain Services (BlueprintPathResolver/Operations), no domain events
- *ddd-architecture*: Application layer (LoadBlueprint/GetValue/SetValue/RemoveValue), Interface layer (CLI/MCP), Infrastructure (YamlBlueprintStorage)

### 2. PythonGen (代码生成)
**Core Responsibility**: Bidirectional conversion between Python source code and structured models (PackageSpec, ModuleSpec, etc.).

**Key Concepts**:
- `PackageSpec` (聚合根): Represents a Python package, the top-level entry for code generation
- `ModuleSpec` (实体): Represents a `.py` file, has identity via name, supports merge operations
- `SourceCodePort`: Abstracts AST parsing/rendering (implemented by AstTranslator)
- `CodeFormatter`: Abstracts code formatting (implemented by BlackCodeFormatter)
- `DependencyResolver`: Resolves module imports from global registry

**Design Doc Summary**:
- *ddd-strategic*: PackageSpec ↔ Python source bidirectional translation; ACL via ports
- *ddd-tactical*: Single aggregate (PackageSpec), ModuleSpec as entity, Value Objects (ClassSpec, FunctionSpec, etc.), Domain Services (DependencyResolver, PythonSyntaxTranslator)
- *ddd-architecture*: Application layer (ParsePackage, GeneratePackage, GenerateSchemaJson), Infrastructure (AstTranslator, BlackCodeFormatter, OsFileSystemAdapter)

### 3. Orchestration (编排协调)
**Core Responsibility**: Coordinates DomainDefinition and PythonGen contexts, transforming CLI commands into cross-context workflows.

**Key Concepts**:
- `BuildResult` (聚合根): Manages build status, file results, and statistics
- `GenerateProject`: Command that orchestrates LoadBlueprint → GeneratePackage
- `GenerateBlueprint`: Command that orchestrates ParsePackage → UpdateBlueprint

**Design Doc Summary**:
- *ddd-strategic*: Acts as conductor; OHS pattern for CLI/MCP interfaces
- *ddd-tactical*: Single aggregate (BuildResult), Value Objects (FileResult, BuildStats, BuildStatus), Domain Services (TestSkeletonMapper), no domain ports
- *ddd-architecture*: Application layer (GenerateProject, GenerateBlueprint), Interface layer (CLI via Typer, MCP via FastMCP), Infrastructure (dependency-injector, Rich for output)

## Special Rules and Context
- **Context-Dependent Source of Truth**:
  - **For the `DomainDefinition` context (Core Models)**: The Python source code (in `src/codegen/domain_definition/`) is the absolute source of truth. When modifying or adding new domain component types or blueprint structures, you must modify the Python Pydantic models first. The generator cannot bootstrap its own domain models. After updating the Python models, run `codegen reverse` to update `codegen.yaml` and `codegen schema` to update `codegen.schema.json`.
  - **For other contexts / normal usage**: The `codegen.yaml` file is the absolute source of truth. Changes to those domain architectures should be reflected in the YAML first (or managed via `codegen add/update/delete` commands) to generate the corresponding code.
- **Naming Conventions**: Different parts of the code require specific casing. Pay attention to how `case-converter` or the custom string types (e.g., `NamingString`) are used to transform names between string representations.
