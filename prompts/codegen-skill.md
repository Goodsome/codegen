---
name: codegen
description: Domain-Driven Design (DDD) code generation from codegen.yaml blueprint. Use when starting new Python projects, designing domain models, or generating DDD boilerplate code.
origin: user
---

# Codegen - DDD Code Generation Tool

Blueprint-driven Python code generator following Domain-Driven Design patterns. Define your domain model in `codegen.yaml`, generate clean architecture code automatically.

## When to Activate

- Starting a new Python project with DDD architecture
- Designing bounded contexts, aggregates, entities, or value objects
- Creating repository ports and infrastructure implementations
- Generating application use cases and services
- Reverse-engineering existing Python code into a blueprint
- Managing domain model evolution via MCP tools

## MCP Tools Available

The following MCP tools are available via `mcp__codegen__*`:

| Tool | Description |
|------|-------------|
| `build` | Compile `codegen.yaml` into Python code |
| `reverse` | Reverse-engineer Python code into `codegen.yaml` |
| `tree` | Display blueprint structure as visual tree |
| `get` | Query a value from blueprint by path |
| `set` | Set or update a value in blueprint by path |
| `rm` | Remove a value from blueprint by path |

### Tool Selection Guide: `tree` vs `get`

Use **`tree`** for global structure exploration:
- Viewing the entire project hierarchy
- Understanding context boundaries and relationships
- Finding what entities/aggregates exist without knowing exact paths
- Exploring structure with optional depth control (`depth: 3`)
- Answering "what is in this project?"

Use **`get`** for leaf node details:
- Getting specific attribute definitions
- Retrieving exact field values at known paths
- Querying single values (e.g., `contexts.Billing.domain.aggregates.Order.attributes`)
- Accessing enum members, behavior signatures, or port definitions
- Answering "what are the details of X?"

**Decision Rule**:
- `tree` = "show me the map" → hierarchical, exploratory
- `get` = "tell me about X" → specific, targeted queries

## Core Workflow

### 1. Initialize Blueprint

Create `codegen.yaml` in your project root:

```yaml
# yaml-language-server: $schema=./codegen.schema.json
name: MyProject
description: Project description
contexts:
  - name: MyContext
    domain:
      aggregates: []
      entities: []
      value_objects: []
      enums: []
    application:
      use_cases: []
      services: []
      ports: []
    infrastructure:
      implementations: []
```

### 2. Define Domain Model

Use MCP tools to build your domain model:

```
# View current structure
mcp__codegen__tree(work_dir="/path/to/project")

# Add a new context
mcp__codegen__set(
  work_dir="/path/to/project",
  path="contexts[-]",
  value='{"name": "Billing", "description": "Payment processing"}'
)

# Add an aggregate
mcp__codegen__set(
  work_dir="/path/to/project",
  path="contexts.Billing.domain.aggregates[-]",
  value='{"name": "Order", "description": "Customer order aggregate"}'
)

# Add entity attributes
mcp__codegen__set(
  work_dir="/path/to/project",
  path="contexts.Billing.domain.aggregates.Order.attributes",
  value='[{"name": "id", "type": "uuid"}, {"name": "status", "type": "string"}]'
)
```

### 3. Generate Code

```
mcp__codegen__build(work_dir="/path/to/project")
```

When targeting specific leaf nodes (filename/component), overwrite mode is automatically enabled. Pass a comma-separated list to generate multiple nodes at once:

```
mcp__codegen__build(work_dir="/path/to/project", node="Order")
mcp__codegen__build(work_dir="/path/to/project", node="CreateOrder,UpdateOrder,DeleteOrder")
```

This generates:
- `src/<context>/domain/` - Aggregates, Entities, Value Objects, Enums
- `src/<context>/application/` - Use Cases, Services, Ports
- `src/<context>/infrastructure/` - Implementations

## Blueprint Structure Reference

### Bounded Context

```yaml
contexts:
  - name: Billing
    description: Payment and invoice management
    domain:
      aggregates: [...]      # Root entities managing consistency
      entities: [...]        # Domain objects with identity
      value_objects: [...]   # Immutable values without identity
      enums: [...]           # Enumeration types
    application:
      use_cases: [...]       # Application-specific operations
      services: [...]        # Domain services
      ports: [...]           # Interface definitions
    infrastructure:
      implementations: [...] # Concrete implementations
```

### Aggregate

```yaml
aggregates:
  - name: Order
    description: Customer order aggregate root
    attributes:
      - name: id
        type: uuid
      - name: customer_id
        type: uuid
      - name: total
        type: float
    behaviors:
      - name: calculate_total
        inputs:
          - name: items
            type: list
        output:
          type: float
```

### Entity

```yaml
entities:
  - name: OrderItem
    description: Individual order line item
    attributes:
      - name: id
        type: uuid
      - name: product_id
        type: uuid
      - name: quantity
        type: integer
      - name: price
        type: float
```

### Value Object

```yaml
value_objects:
  - name: Money
    description: Monetary value with currency
    attributes:
      - name: amount
        type: float
      - name: currency
        type: string
    behaviors:
      - name: add
        inputs:
          - name: other
            type: Money
        output:
          type: Money
```

### Enum

```yaml
enums:
  - name: OrderStatus
    description: Order lifecycle states
    members:
      - name: PENDING
        value: pending
      - name: CONFIRMED
        value: confirmed
      - name: SHIPPED
        value: shipped
      - name: DELIVERED
        value: delivered
```

### Port (Interface)

```yaml
ports:
  - name: OrderRepository
    kind: repository
    aggregate: Order
    behaviors:
      - name: find_by_id
        inputs:
          - name: id
            type: uuid
        output:
          type: Order
      - name: save
        inputs:
          - name: order
            type: Order
```

### Use Case

```yaml
use_cases:
  - name: CreateOrder
    kind: command
    description: Create a new customer order
    inputs:
      - name: customer_id
        type: uuid
      - name: items
        type: list
    output:
      type: Order
```

### Implementation

```yaml
implementations:
  - name: SqlAlchemyOrderRepository
    implements: OrderRepository
    tech: sqlalchemy
    description: PostgreSQL persistence using SQLAlchemy
```

## Path Syntax for MCP Tools

The `get`, `set`, `rm` tools use dot-notation paths:

| Path | Description |
|------|-------------|
| `name` | Project name |
| `contexts` | List of all contexts |
| `contexts[0]` | First context by index |
| `contexts.Billing` | Context named "Billing" |
| `contexts.Billing.domain.aggregates` | All aggregates in Billing |
| `contexts.Billing.domain.aggregates[-]` | Append to aggregates list |
| `contexts.Billing.domain.aggregates.Order.attributes` | Order's attributes |

## Type System

### Primitive Types

- `string`, `integer`, `float`, `boolean`, `uuid`, `datetime`, `any`

### Container Types

- `none` (default) - Single value
- `list` - `List[T]`
- `set` - `Set[T]`
- `map` - `Dict[K, V]`

### Custom Types

Reference other domain objects by name:

```yaml
attributes:
  - name: customer
    type: Customer          # Reference to Entity
  - name: items
    type: OrderItem
    container: list         # List[OrderItem]
```

## Best Practices

### 1. Single Source of Truth

`codegen.yaml` is the authoritative definition for generated contexts (except `DomainDefinition` context which bootstraps the generator itself).

### 2. Naming Conventions

- **Contexts**: PascalCase (e.g., `Billing`, `OrderManagement`)
- **Aggregates/Entities**: PascalCase (e.g., `Order`, `Customer`)
- **Value Objects**: PascalCase (e.g., `Money`, `Address`)
- **Use Cases**: PascalCase verb phrases (e.g., `CreateOrder`, `ProcessPayment`)
- **Ports**: PascalCase with suffix (e.g., `OrderRepository`, `PaymentGateway`)
- **Methods/Behaviors**: snake_case (e.g., `calculate_total`, `process_payment`)

### 3. Aggregate Design

- Keep aggregates small and focused
- Aggregates enforce consistency boundaries
- Reference other aggregates by ID, not by object

### 4. Layer Separation

- **Domain**: Pure business logic, no infrastructure concerns
- **Application**: Orchestrates use cases, calls domain and ports
- **Infrastructure**: Implements ports with concrete technologies

### 5. Reverse Engineering

When adapting existing Python code:

```
mcp__codegen__reverse(
  work_dir="/path/to/project",
  package_path="src/my_package"
)
```

## Generated Code Structure

```
src/
├── my_package/
│   ├── __init__.py
│   ├── bootstrap.py              # DI container setup
│   ├── MyContext/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── aggregates/
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   └── enums/
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── use_cases/
│   │   │   ├── services/
│   │   │   └── ports/
│   │   └── infrastructure/
│   │       ├── __init__.py
│   │       └── implementations/
```

## Common Workflows

### Add New Aggregate

```
# 1. Define aggregate
mcp__codegen__set(
  work_dir="/path",
  path="contexts.Sales.domain.aggregates[-]",
  value='{"name": "Product", "attributes": [{"name": "id", "type": "uuid"}, {"name": "name", "type": "string"}]}'
)

# 2. Add repository port
mcp__codegen__set(
  work_dir="/path",
  path="contexts.Sales.application.ports[-]",
  value='{"name": "ProductRepository", "kind": "repository", "aggregate": "Product"}'
)

# 3. Generate code (use --node to overwrite existing component, comma-separated for multiple)
mcp__codegen__build(work_dir="/path", node="Product")
```

### Add Use Case

```
mcp__codegen__set(
  work_dir="/path",
  path="contexts.Sales.application.use_cases[-]",
  value='{"name": "ListProducts", "kind": "query", "description": "List all products"}'
)

mcp__codegen__build(work_dir="/path", node="ListProducts")
```

### Remove Component

```
mcp__codegen__rm(
  work_dir="/path",
  path="contexts.Sales.domain.entities.OldEntity"
)

mcp__codegen__build(work_dir="/path", node="OldEntity")
```

## Troubleshooting

### Schema Validation

Ensure your IDE uses `codegen.schema.json` for validation:

```yaml
# yaml-language-server: $schema=./codegen.schema.json
```

### Generation Errors

1. Use `mcp__codegen__tree` to inspect overall structure (what contexts/aggregates exist)
2. Use `mcp__codegen__get` to verify specific component details (are attributes correct?)
3. Check YAML syntax against schema

### Missing Dependencies

Generated code requires:
- Python 3.13+
- `pydantic` for models
- `dependency-injector` for DI
- `case-converter` for naming

---

**Note**: This tool is most effective when used iteratively - define small increments, generate, review, and extend.