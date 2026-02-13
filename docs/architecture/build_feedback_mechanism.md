# Architecture: Build Feedback Mechanism

## Status
Proposed

## Context
Code generation is a critical part of the workflow. Users (both human CLI users and AI agents) need detailed feedback on what happened during the build process.
Currently, the `GeneratePackage` and `GenerateProject` use cases return a simple `str` (often just "Success") or empty output.
This lack of visibility makes it difficult to:
1. Verify which files were actually modified.
2. Understand why a file was skipped (e.g. no changes detected).
3. Debug failures in specific file generations.
4. Verify the impact of a blueprint change.

## Decision
We will introduce a structured `BuildResult` to the `Orchestration` domain. This structure will provide granular details about the generation process.

### 1. Domain Models (Orchestration context)

We will introduce the following value objects and enums in the `Orchestration` context:

#### Enums
*   **BuildStatus**: `SUCCESS`, `FAILURE`, `WARNING`
*   **FileStatus**: `CREATED`, `UPDATED`, `SKIPPED`, `FAILED`

#### Value Objects
*   **FileResult**: Represents the outcome for a single file.
    *   `path`: str (Relative path from project root)
    *   `status`: FileStatus
    *   `message`: str (Optional, e.g. "No changes detected", specific error message)
    *   `diff`: str (Optional, for future use, potentially showing diffs)

*   **BuildStats**: Aggregated statistics.
    *   `total_files`: int
    *   `created_count`: int
    *   `updated_count`: int
    *   `skipped_count`: int
    *   `failed_count`: int
    *   `duration_ms`: int

*   **BuildResult**: The top-level result object.
    *   `status`: BuildStatus
    *   `files`: list[FileResult]
    *   `stats`: BuildStats
    *   `messages`: list[str] (Global messages or warnings)

### 2. Use Case Updates

The following use cases in `Orchestration` application layer will be updated to return `BuildResult`:

*   `GeneratePackage`
    *   Current: `result: str`
    *   New: `result: BuildResult`

*   `GenerateProject`
    *   Current: `result: str`
    *   New: `result: BuildResult`

### 3. Implementation Details

*   **ExecutionContainer**: The build command handler must aggregate results from the `Generator` strategy.
*   **GeneratorStrategy**: The underlying generation logic (`PythonSyntaxTranslator`, `JinjaAdapter`, etc.) needs to report back status for each file operation.
*   **CLI / MCP**: The presentation layer will need to interpret `BuildResult`.
    *   CLI: Render a rich table (using `rich` library) showing modified files and stats.
    *   MCP: Return the full JSON object so agents can analyze it.

## Consequences

### Positive
*   **Observability**: Complete visibility into the build process.
*   **Debuggability**: Easier to identify which specific file failed and why.
*   **Agentic Workflow**: Agents can verify their work by checking if expected files were `CREATED` or `UPDATED`.

### Negative
*   **Complexity**: The implementation of `GeneratePackage` becomes more complex as it needs to track state.
*   **Breaking Change**: Consumers of `GeneratePackage` (e.g. CLI tests) will need to be updated to handle the new return type.
