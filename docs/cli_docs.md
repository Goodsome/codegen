# `codegen`

A DDD (Domain-Driven Design) Project Scaffolding Tool.

Codegen reads a codegen.yaml blueprint file that defines your project structure
and generates Python code based on DDD patterns. It can also reverse-engineer
existing Python packages back into a codegen.yaml blueprint.

Common commands:
- codegen generate              Generate code from codegen.yaml
- codegen generate-blueprint    Reverse engineer Python package to blueprint
- codegen generate-blueprint-schema  Generate JSON schema for blueprint
    

For more information, see: https://github.com/Goodsome/codegen

**Usage**:

```console
$ codegen [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `generate`: Generate Python code from a codegen.yaml...
* `generate-blueprint`: Reverse engineer an existing Python...
* `generate-blueprint-schema`: Generate JSON schema for codegen.yaml...
* `add`: Add components to the blueprint
* `update`: Update existing components
* `delete`: Delete components

## `codegen generate`

Generate Python code from a codegen.yaml blueprint.

**Usage**:

```console
$ codegen generate [OPTIONS]
```

**Options**:

* `--overwrite`: Overwrite existing files without prompting
* `--build / --no-build`: Output to src directory (default: --build). Use --no-build to output to target directory  [default: build]
* `--node TEXT`: Generate only a specific bounded context or component by name (e.g., &#x27;DomainDefinition&#x27;)
* `-c, --config PATH`: Path to the codegen.yaml blueprint file (default: codegen.yaml in current directory)  [default: codegen.yaml]
* `--out PATH`: Custom output directory (overrides --build/--no-build default locations)
* `--help`: Show this message and exit.

## `codegen generate-blueprint`

Reverse engineer an existing Python package into a codegen.yaml blueprint.

**Usage**:

```console
$ codegen generate-blueprint [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Path to output codegen.yaml blueprint file  [default: codegen.yaml]
* `--package PATH`: Path to existing Python package to reverse engineer (default: auto-detect from src/)
* `--help`: Show this message and exit.

## `codegen generate-blueprint-schema`

Generate JSON schema for codegen.yaml blueprint validation.

**Usage**:

```console
$ codegen generate-blueprint-schema [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `codegen add`

Add components to the blueprint

**Usage**:

```console
$ codegen add [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `context`: Add a new Bounded Context.
* `aggregate`: Add a new Aggregate.
* `entity`: Add a new Entity.
* `value-object`: Add a new Value Object.
* `service`: Add a new Domain Service.
* `enum`: Add a new Enum.
* `port`: Add a new Port.
* `implementation`: Add a new Infrastructure Implementation.
* `use-case`: Add a new Use Case.
* `method`: Add a method to a Service, Aggregate,...
* `member`: Add a member to an Enum.

### `codegen add context`

Add a new Bounded Context.

**Usage**:

```console
$ codegen add context [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Bounded Context  [required]

**Options**:

* `-d, --desc TEXT`: Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add aggregate`

Add a new Aggregate.

**Usage**:

```console
$ codegen add aggregate [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Aggregate  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: Description
* `-a, --attr TEXT`: Attributes in format &#x27;name:type:optional&#x27;
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add entity`

Add a new Entity.

**Usage**:

```console
$ codegen add entity [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Entity  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: Description
* `-a, --attr TEXT`: Attributes in format &#x27;name:type:optional&#x27;
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add value-object`

Add a new Value Object.

**Usage**:

```console
$ codegen add value-object [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Value Object  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: Description
* `-a, --attr TEXT`: Attributes in format &#x27;name:type:optional&#x27;
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add service`

Add a new Domain Service.

**Usage**:

```console
$ codegen add service [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Service  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add enum`

Add a new Enum.

**Usage**:

```console
$ codegen add enum [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Enum  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add port`

Add a new Port.

**Usage**:

```console
$ codegen add port [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Port  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-k, --kind TEXT`: Port Type: repository, client, provider, adapter  [required]
* `-d, --desc TEXT`: Description
* `-agg, --aggregate TEXT`: Related Aggregate (required for repositories)
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add implementation`

Add a new Infrastructure Implementation.

**Usage**:

```console
$ codegen add implementation [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Implementation  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-t, --tech TEXT`: Technology/Library (e.g. sqlalchemy)  [required]
* `-i, --implements TEXT`: Interface name implemented by this component  [required]
* `-d, --desc TEXT`: Description
* `-a, --attr TEXT`: Attributes in format &#x27;name:type:optional&#x27;
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add use-case`

Add a new Use Case.

**Usage**:

```console
$ codegen add use-case [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Use Case  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-k, --kind TEXT`: Use Case Type: command, query  [required]
* `-d, --desc TEXT`: Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add method`

Add a method to a Service, Aggregate, Implementation, or Port.

**Usage**:

```console
$ codegen add method [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Method  [required]

**Options**:

* `--on TEXT`: Name of the parent component (Service, Aggregate, Implementation, Port)  [required]
* `--context TEXT`: Target Bounded Context  [required]
* `--type TEXT`: Type of parent component: service, aggregate, implementation, port  [required]
* `--arg TEXT`: Arguments in format &#x27;name:type:optional&#x27;
* `--return, --ret TEXT`: Return type  [default: None]
* `-d, --desc TEXT`: Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen add member`

Add a member to an Enum.

**Usage**:

```console
$ codegen add member [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Enum Member  [required]

**Options**:

* `--on TEXT`: Name of the Enum  [required]
* `--context TEXT`: Target Bounded Context  [required]
* `--value TEXT`: Value of the member (optional)
* `-d, --desc TEXT`: Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

## `codegen update`

Update existing components

**Usage**:

```console
$ codegen update [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `aggregate`
* `entity`
* `value-object`
* `port`
* `implementation`: Update an Infrastructure Implementation.
* `use-case`: Update a Use Case.
* `method`: Update a method description.
* `member`: Update an Enum Member.

### `codegen update aggregate`

**Usage**:

```console
$ codegen update aggregate [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Aggregate  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: New Description
* `-a, --add-attr TEXT`: Add attributes &#x27;name:type&#x27;
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen update entity`

**Usage**:

```console
$ codegen update entity [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Entity  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: New Description
* `-a, --add-attr TEXT`: Add attributes &#x27;name:type&#x27;
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen update value-object`

**Usage**:

```console
$ codegen update value-object [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Value Object  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: New Description
* `-a, --add-attr TEXT`: Add attributes &#x27;name:type&#x27;
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen update port`

**Usage**:

```console
$ codegen update port [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Port  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: New Description
* `-k, --kind TEXT`: New Port Type
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen update implementation`

Update an Infrastructure Implementation.

**Usage**:

```console
$ codegen update implementation [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Implementation  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: New Description
* `-a, --add-attr TEXT`: Add attributes &#x27;name:type&#x27;
* `-t, --tech TEXT`: New Technology
* `-i, --implements TEXT`: New Interface implemented
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen update use-case`

Update a Use Case.

**Usage**:

```console
$ codegen update use-case [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Use Case  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-d, --desc TEXT`: New Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen update method`

Update a method description.

**Usage**:

```console
$ codegen update method [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Method  [required]

**Options**:

* `--on TEXT`: Name of the parent component  [required]
* `--context TEXT`: Target Bounded Context  [required]
* `--type TEXT`: Type of parent component: service, aggregate, implementation, port  [required]
* `-d, --desc TEXT`: New Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen update member`

Update an Enum Member.

**Usage**:

```console
$ codegen update member [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Enum Member  [required]

**Options**:

* `--on TEXT`: Name of the Enum  [required]
* `--context TEXT`: Target Bounded Context  [required]
* `--value TEXT`: New Value
* `-d, --desc TEXT`: New Description
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

## `codegen delete`

Delete components

**Usage**:

```console
$ codegen delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `context`
* `aggregate`
* `entity`
* `value-object`
* `service`
* `enum`
* `port`
* `implementation`
* `use-case`
* `method`: Delete a method from a Service, Aggregate,...
* `member`: Delete a member from an Enum.

### `codegen delete context`

**Usage**:

```console
$ codegen delete context [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Bounded Context  [required]

**Options**:

* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete aggregate`

**Usage**:

```console
$ codegen delete aggregate [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Aggregate  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete entity`

**Usage**:

```console
$ codegen delete entity [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Entity  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete value-object`

**Usage**:

```console
$ codegen delete value-object [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Value Object  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete service`

**Usage**:

```console
$ codegen delete service [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Service  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete enum`

**Usage**:

```console
$ codegen delete enum [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Enum  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete port`

**Usage**:

```console
$ codegen delete port [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Port  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete implementation`

**Usage**:

```console
$ codegen delete implementation [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Implementation  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete use-case`

**Usage**:

```console
$ codegen delete use-case [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Use Case  [required]

**Options**:

* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete method`

Delete a method from a Service, Aggregate, Implementation, or Port.

**Usage**:

```console
$ codegen delete method [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Method  [required]

**Options**:

* `--on TEXT`: Name of the parent component  [required]
* `--context TEXT`: Target Bounded Context  [required]
* `--type TEXT`: Type of parent component: service, aggregate, implementation, port  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.

### `codegen delete member`

Delete a member from an Enum.

**Usage**:

```console
$ codegen delete member [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the Enum Member  [required]

**Options**:

* `--on TEXT`: Name of the Enum  [required]
* `--context TEXT`: Target Bounded Context  [required]
* `-c, --config PATH`: Path to the codegen.yaml blueprint file  [default: codegen.yaml]
* `--help`: Show this message and exit.
