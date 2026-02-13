# Detailed Design: Build Feedback Mechanism Implementation

## 1. Context
Based on `docs/architecture/build_feedback_mechanism.md`, we need to implement a structured feedback mechanism for the code generation process. This document details the data structures, interface changes, and interaction logic required to support `BuildResult`.

## 2. Data Models (Domain Layer)

We will define these models in `contexts.Orchestration.domain`.

### 2.1 Enums

```python
from enum import Enum

class BuildStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"  # Critical failure (e.g. blueprint not found)
    WARNING = "WARNING"  # Partial success (some files failed)

class FileStatus(Enum):
    CREATED = "CREATED"  # New file generated
    UPDATED = "UPDATED"  # Existing file changed
    SKIPPED = "SKIPPED"  # No changes detected or identical content
    FAILED = "FAILED"    # Error during generation for this file
```

### 2.2 Value Objects (DTOs)

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class FileResult(BaseModel):
    """Represents the outcome for a single file generation."""
    path: str = Field(..., description="Relative path from project root")
    status: FileStatus
    message: Optional[str] = Field(None, description="Reason for skip or error message")
    diff: Optional[str] = Field(None, description="Unified diff if updated")

class BuildStats(BaseModel):
    """Aggregated statistics for a build operation."""
    total_files: int = 0
    created_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    duration_ms: int = 0

    def add_result(self, result: FileResult):
        self.total_files += 1
        if result.status == FileStatus.CREATED:
            self.created_count += 1
        elif result.status == FileStatus.UPDATED:
            self.updated_count += 1
        elif result.status == FileStatus.SKIPPED:
            self.skipped_count += 1
        elif result.status == FileStatus.FAILED:
            self.failed_count += 1

class BuildResult(BaseModel):
    """Top-level result object returned by generation use cases."""
    status: BuildStatus
    files: List[FileResult] = Field(default_factory=list)
    stats: BuildStats = Field(default_factory=BuildStats)
    messages: List[str] = Field(default_factory=list)

    def add_file_result(self, result: FileResult):
        self.files.append(result)
        self.stats.add_result(result)
        # Update overall status based on file result
        if result.status == FileStatus.FAILED:
            self.status = BuildStatus.WARNING
```

## 3. Interface Updates

### 3.1 Generator Strategy Interface

The `GeneratorStrategy` (and its implementations like `JinjaGenerator`, `PythonGenerator`) needs to change from returning `void` (or implicitly creating files) to returning `FileResult`.

```python
from abc import ABC, abstractmethod

class GeneratorStrategy(ABC):
    @abstractmethod
    def generate(self, context: dict, output_path: str) -> FileResult:
        """
        Generates a file based on context and writes to output_path.
        
        Returns:
            FileResult: The outcome of the generation.
        """
        pass
```

### 3.2 Application Use Cases

The `code_generator` service (which likely contains `GeneratePackage` and `GenerateProject`) needs to be updated.

#### GeneratePackage

```python
class GeneratePackage:
    def execute(self, package_name: str) -> BuildResult:
        # ... logic ...
        pass
```

#### GenerateProject

```python
class GenerateProject:
    def execute(self) -> BuildResult:
        # ... logic ...
        pass
```

## 4. Interaction Logic & Implementation Flow

### 4.1 Orchestrator / Use Case Logic

The `GeneratePackage` use case will act as the orchestrator.

**Pseudo-code Flow:**

```python
def execute(self, package_name: str) -> BuildResult:
    start_time = time.time()
    build_result = BuildResult(status=BuildStatus.SUCCESS)
    
    try:
        # 1. Load Blueprint
        blueprint = self.blueprint_repo.get(package_name)
        
        # 2. Identify files to generate
        # (Assuming we have a list of definitions or nodes to iterate)
        definitions = blueprint.get_definitions()
        
        for definition in definitions:
            try:
                # 3. Delegate to specific generator
                # The generator is responsible for:
                #   - Checking if file exists
                #   - Comparing content (for SKIPPED status)
                #   - Writing file (if CREATED or UPDATED)
                file_result = self.generator.generate(definition)
                
                build_result.add_file_result(file_result)
                
            except Exception as e:
                # 4. Partial Failure Handling
                # Capture the error for this specific file, but continue with others
                error_result = FileResult(
                    path=definition.suggested_path,
                    status=FileStatus.FAILED,
                    message=str(e)
                )
                build_result.add_file_result(error_result)
                
    except Exception as e:
        # 5. Critical Failure Handling
        build_result.status = BuildStatus.FAILURE
        build_result.messages.append(f"Critical error: {str(e)}")
        
    finally:
        build_result.stats.duration_ms = int((time.time() - start_time) * 1000)
        
    return build_result
```

### 4.2 Generator Implementation Logic

The `Generator` implementations must handle the logic for `SKIPPED` vs `UPDATED`.

**Pseudo-code for `StandardGenerator.generate`:**

```python
def generate(self, definition) -> FileResult:
    target_path = definition.get_path()
    rendered_content = self.render_template(definition)
    
    if not os.path.exists(target_path):
        self.file_system.write(target_path, rendered_content)
        return FileResult(path=target_path, status=FileStatus.CREATED)
        
    current_content = self.file_system.read(target_path)
    
    if current_content == rendered_content:
        return FileResult(path=target_path, status=FileStatus.SKIPPED, message="No changes")
        
    # Content differs
    self.file_system.write(target_path, rendered_content)
    # Optional: Calculate diff here if needed
    return FileResult(path=target_path, status=FileStatus.UPDATED)
```

## 5. Error Handling Strategy

1.  **Critical Errors**: (e.g., Database down, Blueprint syntax error) -> `BuildStatus.FAILURE`. The `messages` list will contain the panic reason.
2.  **Partial Errors**: (e.g., Jinja template error for one file, File permission error) -> `BuildStatus.WARNING`. The specific file will be marked `FAILED` in `files` list. The process **should continue** to generate other files if possible.
