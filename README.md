# Codegen

Codegen is a powerful CLI tool designed to facilitate Domain-Driven Design (DDD) by generating boilerplate code from a structured blueprint (`codegen.yaml`). It helps maintain a clean architecture by managing contexts, domain models, application logic, and infrastructure configurations.

## Features

- **Blueprint-Driven Development**: Define your domain model in `codegen.yaml`.
- **DDD Architecture**: Automatically structures code into Domain, Application, and Infrastructure layers.
- **CLI Management**: Easily add, update, and delete components directly from the command line.
- **Extensible**: Supports custom templates and language generation (currently focused on Python).

## Installation

Prerequisites: Python 3.10+

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Codegen
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

## Usage

The `codegen` CLI is the main entry point for all operations.

### 1. Generating Code

To generate code based on your current `codegen.yaml` blueprint:

```bash
codegen generate
```

To use a specific blueprint file:

```bash
codegen generate --config my-blueprint.yaml
```

### 2. Managing Components

You can manage your DDD components without manually editing the YAML file.

#### Bounded Contexts
```bash
# Add a new context
codegen add context Billing --desc "Handles payments and invoices"

# Delete a context
codegen delete context Billing
```

#### Domain Components
Supported types: `aggregate`, `entity`, `value-object`, `service`, `enum`, `port`.

```bash
# Add an Aggregate
codegen add aggregate Order --context Billing --desc "Customer order" --attr "id:string:required"

# Add a Repository Port
codegen add port OrderRepository --context Billing --kind repository --aggregate Order

# Update an Entity
codegen update entity OrderItem --context Billing --add-attr "quantity:int"
```

#### Application Components
Manage use cases for your application logic.

```bash
# Add a Command
codegen add use-case CreateOrder --context Billing --kind command --desc "Creates a new order"

# Update a Use Case
codegen update use-case CreateOrder --context Billing --desc "New description"
```

#### Infrastructure Implementations
Manage specific implementations for your ports.

```bash
# Add an Implementation (e.g., SQLAlchemy Repository)
codegen add implementation PostgresOrderRepo --context Billing --tech sqlalchemy --implements OrderRepository

# Update Implementation details
codegen update implementation PostgresOrderRepo --context Billing --desc "Async Postgres Repo"
```

#### Deleting Components
```bash
codegen delete value-object Money --context Billing
codegen delete implementation PostgresOrderRepo --context Billing
```

### 3. Help

For a full list of commands and options:

```bash
codegen --help
codegen add --help
codegen update --help
```

## Project Structure

- `codegen.yaml`: The single source of truth for your domain definitions.
- `src/codegen/`: Core logic for the generator.
- `src/codegen/cli/`: CLI implementation using Typer.
- `src/codegen/domain_definition/`: parsers and models for the blueprint.

## Development

To interpret the CLI commands for debugging or verification:

```bash
python verify_cli.py
```
