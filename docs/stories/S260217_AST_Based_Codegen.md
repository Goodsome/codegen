# User Story: Based on Infrastructure Layer AST Code Generator Implementation

## User Story
**As a** Developer,
**I want to** create a new Translator in the Infrastructure layer to convert PythonGen Spec objects directly into Python ast nodes, and use `ast.unparse` to generate final code, completely removing dependency on Jinja2 templates,
**So that** I can obtain more robust code generation capabilities (automatic indentation handling, syntax checking), while ensuring the PythonGen domain model does not contain specific AST construction logic, keeping the architecture clean.

## Context
Currently, code generation relies on Jinja2 templates which can be brittle regarding indentation and syntax errors. Moving to an AST-based approach allows for programmatic code construction guarantees valid syntax and proper formatting.

## Key Requirements
1.  **Infrastructure Layer**: The AST construction logic must reside here, acting as an Anti-Corruption Layer (ACL) or Adapter for the Domain output.
2.  **Input**: PythonGen Spec objects (Domain layer).
3.  **Output**: Python Source Code (String).
4.  **Mechanism**: Spec -> `ast.Module` / `ast.AST` -> `ast.unparse()`.
5.  **Separation of Concerns**: Domain objects must NOT depend on the `ast` module.
