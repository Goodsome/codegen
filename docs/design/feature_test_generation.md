# Test Generation Feature Design

## 1. Context and Goals
The goal is to automate the creation of unit tests for UseCases and Domain entities. This feature aims to reduce boilerplate code and encourage high test coverage by providing ready-to-run test skeletons.

Initially, the scope includes:
- **UseCase Unit Tests**: Automatically mocking Ports and Services.
- **Configuration**: allowing users to enable/disable tests and choose mocking strategies via `codegen.yaml`.

## 2. Metamodel Changes
We need to capture user preferences for test generation. The following schema changes are proposed for the `DomainDefinition` context in `codegen.yaml`.

### 2.1 New Enum: `TestMockStrategy`
Defines the library/pattern used for mocking dependencies.

| Member     | Value      | Description                                      |
|------------|------------|--------------------------------------------------|
| `UNITTEST` | `unittest` | Use the standard library `unittest.mock`.        |
| `PYTEST`   | `pytest`   | Use `pytest-mock` (`mocker` fixture).            |

### 2.2 New Value Object: `TestConfig`
Holds configuration parameters for test generation.

| Attribute       | Type               | Description                                      | Default  |
|-----------------|--------------------|--------------------------------------------------|----------|
| `enabled`       | `bool`             | Whether test generation is active.               | `True`   |
| `strategy`      | `TestMockStrategy` | The mocking strategy to use.                     | `PYTEST` |
| `fixtures_path` | `str` (Optional)   | Path to shared fixtures (e.g., `conftest.py`).   | `None`   |

### 2.3 Updated Value Object: `Blueprint`
Update the root `Blueprint` object to include a global test configuration.

- **Attribute**: `test_config`
- **Type**: `TestConfig` (Optional)

### 2.4 Updated Value Object: `BoundedContext`
Update `BoundedContext` to include a context-level override for test configuration.

- **Attribute**: `test_config`
- **Type**: `TestConfig` (Optional)

## 3. Generation Logic

### 3.1 UseCase Test Generation
This is the primary focus. The generator will inspect the UseCase dependencies and generate a corresponding test file.

- **Target Path**: `tests/{context_name}/application/use_cases/test_{use_case_name}.py`

#### Input Analysis
1.  **Read `UseCaseSpec`**: Identify the UseCase class name and its location.
2.  **Extract Dependencies**: Iterate through `dependencies` (usually Ports or Domain Services).
3.  **Identify Inputs**: Determine the `command` or `query` DTO class required for the `execute` method.

#### Code Structure (Template)
The generator must support the selected `TestMockStrategy`.

**Example (Strategy: PYTEST)**:
```python
import pytest
from unittest.mock import create_autospec
from {context}.domain.ports import {PortName}
from {context}.application.use_cases import {UseCaseName}
from {context}.application.dtos import {CommandName}

def test_{use_case_name}_success(mocker):
    # Arrange
    mock_{port_name} = mocker.Mock(spec={PortName})
    # Setup default behaviors for mocks if needed
    
    use_case = {UseCaseName}(
        {port_name}=mock_{port_name}
    )
    
    command = {CommandName}(
        # TODO: Fill required fields
        ...
    )

    # Act
    result = use_case.execute(command)

    # Assert
    assert result is not None
    # mock_{port_name}.save.assert_called_once()
```

### 3.2 Domain Test Generation
For Aggregates and Entities, generate basic lifecycle tests.

- **Target Path**: `tests/{context_name}/domain/aggregates/test_{aggregate_name}.py`

#### Logic
- Instantiate the Aggregate.
- Call factory methods (e.g., `create`).
- Assert initial state.

## 4. Implementation Plan

### Step 1: Metamodel Update
- Modify `codegen.yaml` to include `TestMockStrategy` and `TestConfig`.
- Update `Blueprint` and `BoundedContext` definitions.
- Run `codegen build` to update the `DomainDefinition` python code.

### Step 2: Scaffolding Generator
- Modify `codegen.yaml`
- Create a new service `TestGenerator` in the `PythonGen` context.
- Define operations to generating test files based on `ModuleSpec` or `ClassSpec`.

### Step 3: Implement Logic
- Implement the code generation logic using string templates or an AST builder.
- Ensure generic imports are handled identifying the correct package paths.

### Step 4: Integration
- Hook `TestGenerator` into the main `Orchestration` flow.
- Ensure tests are generated alongside the application code.
