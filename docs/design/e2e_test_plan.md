# E2E Test Framework Design

## Overview
This document outlines the design for the End-to-End (E2E) testing framework for the Codegen project.
The goal is to verify the entire code generation pipeline from Blueprint (YAML) to Generated Code (Python).

## Directory Structure
We will introduce a new directory `tests/e2e/` to separate these slow-running, integration-heavy tests from unit tests.

```text
tests/
├── unit/           # Existing unit tests
└── e2e/            # New E2E tests
    ├── __init__.py
    ├── conftest.py          # E2E specific fixtures
    ├── test_codegen_cli.py  # Main test scenarios
    └── fixtures/            # Test data
        └── simple_project/  # Sample project blueprint
            └── codegen.yaml
```

## Test Strategy

### 1. Test Runner
*   We will use standard `pytest`.
*   We can mark these tests with `@pytest.mark.e2e` so they can be included/excluded easily.

### 2. Execution Method
*   **Primary**: Use `typer.testing.CliRunner` (if applicable) or direct invocation of the `main` entry point function. This is faster and easier to debug than `subprocess`.
*   **Secondary**: Occasional `subprocess` test to verify the actual `codegen` command availability in the shell environment (optional for now).

### 3. Fixture Management
*   **`working_dir`**: A `tmp_path` fixture that automatically cleans up after tests.
*   **`sample_blueprint`**: A fixture that copies `tests/e2e/fixtures/simple_project/codegen.yaml` to the `working_dir`.

### 4. Verification Logic
The `ValidationHelper` class will provide methods to assert:
*   `assert_file_exists(path)`: Check if file was generated.
*   `assert_directory_structure(expected_tree)`: Check full tree.
*   `assert_valid_python(path)`: Use `ast.parse(content)` to ensure generated code has valid syntax.

## Scenarios to Implement (MVP)
1.  **Happy Path**: Run generation on `simple_project/codegen.yaml` and verify:
    *   `src/` created.
    *   `pyproject.toml` (if managed) or module roots created.
    *   Domain/App/Infra folders created.
2.  **Dry Run**: Verify `--dry-run` does not create files.
3.  **Idempotency**: Run twice, ensure no errors and files remain valid.

## Implementation Steps (Tasks)
1.  **Setup**: Create `tests/e2e` structure and `conftest.py`.
2.  **Fixtures**: Create valid `simple_project/codegen.yaml`.
3.  **Test Case**: Implement `test_codegen_cli.py`.
