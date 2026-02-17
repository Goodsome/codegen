# Feature: SourceCodePort 双向接口设计与 AST 映射详细规格

> **Status**: Draft
> **Date**: 2026-02-17
> **Ref**: docs/architecture/ast_codegen_design.md

本文档详细定义了 `SourceCodePort` 的双向接口规范，以及 `AstTranslator` 内部 Builders (正向) 和 Parsers (反向) 的具体映射逻辑。目标是实现完全基于 AST 的代码生成与解析，消除 Domain 层对 `ast` 模块的直接依赖。

## 1. SourceCodePort 接口定义

`SourceCodePort` 位于 `codegen.python_gen.domain.ports.source_code_port`，提供统一的 Python 源代码双向转换能力。

```python
from abc import ABC, abstractmethod
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec

class SourceCodePort(ABC):
    """Port for bidirectional translation between Spec objects and Python source code."""

    @abstractmethod
    def render_module(
        self,
        module_spec: ModuleSpec,
        imports: list[ImportFromSpec],
    ) -> str:
        """
        正向生成: 将 ModuleSpec 转换为 Python 源代码字符串。
        
        Args:
            module_spec: 模块定义，包含类、函数、枚举等。
            imports: 需要生成在文件头部的导入列表。
            
        Returns:
            完整的 Python 源代码字符串。
        """
        ...

    @abstractmethod
    def parse_module(
        self,
        source_code: str,
        module_name: str,
    ) -> ModuleSpec:
        """
        反向解析: 将 Python 源代码字符串解析为 ModuleSpec。
        
        Args:
            source_code: Python 源代码内容。
            module_name: 模块名称（不含 .py 后缀）。
            
        Returns:
            解析后的 ModuleSpec 对象。
            
        Raises:
            SyntaxError: 如果 source_code 不是合法的 Python 代码。
            ValueError: 如果代码结构无法映射到 Domain Spec (例如包含不支持的语法结构)。
        """
        ...
```

## 2. AstTranslator 内部架构

`AstTranslator` (Infrastructure Adapter) 将实现上述接口。内部逻辑拆分为 **Builders** (Spec -> AST) 和 **Parsers** (AST -> Spec) 两组纯函数模块。

### 2.1 Directory Structure

```plaintext
src/codegen/python_gen/infrastructure/adapters/
├── ast_translator.py              # 实现 SourceCodePort
├── ast_builders/                  # [Internal] 正向生成逻辑
│   ├── __init__.py
│   ├── module_builder.py
│   ├── class_builder.py
│   ├── function_builder.py
│   ├── enum_builder.py
│   ├── import_builder.py
│   └── type_builder.py
└── ast_parsers/                   # [Internal] 反向解析逻辑
    ├── __init__.py
    ├── module_parser.py
    ├── class_parser.py
    ├── function_parser.py
    ├── enum_parser.py
    ├── import_parser.py
    └── type_parser.py
```

---

## 3. AstBuilders (Spec -> AST) 详细设计

所有 Builder 函数均接收 Spec 对象，返回 `ast.AST` 节点。

### 3.1 `module_builder.build_module`

*   **Input**: `module_spec: ModuleSpec`, `imports: list[ImportFromSpec]`
*   **Output**: `ast.Module`
*   **Logic**:
    1.  创建一个空的 `body: list[ast.stmt] = []`.
    2.  `imports` -> 调用 `import_builder.build_import` -> append to body.
    3.  `module_spec.enums` -> 调用 `enum_builder.build_enum` -> append to body.
    4.  `module_spec.classes` -> 调用 `class_builder.build_class` -> append to body.
    5.  `module_spec.functions` -> 调用 `function_builder.build_function` -> append to body.
    6.  **Edge Case**: 如果 body 为空（例如 `__init__.py`），不需通过 `ModuleSpec` 特殊处理，生成的 `ast.Module` body 为空即可。`ast.unparse` 会生成空字符串。
    7.  Return `ast.Module(body=body, type_ignores=[])`.

### 3.2 `class_builder.build_class`

*   **Input**: `class_spec: ClassSpec`
*   **Output**: `ast.ClassDef`
*   **Logic**:
    1.  `body: list[ast.stmt] = []`.
    2.  **Docstring**: 如果 `class_spec.description` 存在，创建 `ast.Expr(value=ast.Constant(value=...))` 作为 body 第一项。
    3.  **Attributes**: `class_spec.attributes` -> 调用 `function_builder.build_parameter_as_attribute` -> append.
    4.  **Methods**: `class_spec.methods` -> 调用 `function_builder.build_function` -> append.
    5.  **Empty Body**: 如果 body 为空，append `ast.Expr(value=ast.Constant(value=...))`. (注意：使用 `...` (Ellipsis) 比 `pass` 更现代，但在生成的代码中 `pass` 可能兼容性更好，暂定使用 `...`).
    6.  **Bases**: `class_spec.inheritance` -> 遍历，使用 `ast.parse(name, mode='eval').body` 解析为 `ast.Name` 或 `ast.Attribute`.
    7.  **Decorators**: `class_spec.decorators` -> 遍历，同上解析.
    8.  Return `ast.ClassDef`.

### 3.3 `function_builder.build_function`

*   **Input**: `func_spec: FunctionSpec`
*   **Output**: `ast.FunctionDef | ast.AsyncFunctionDef`
*   **Logic**:
    1.  **Args**:
        *   如果 `is_instance_method()` 为 True，首个参数通过 `ast.arg(arg='self')` 添加。
        *   遍历 `func_spec.parameters`，调用 `build_parameter`。
        *   构建 `ast.arguments`.
    2.  **Body**:
        *   如果 `func_spec.suite` 存在，使用 `ast.parse(func_spec.suite).body` 解析代码片段。
            *   **Risk**: `suite` 必须是缩进无关的语句块。由于 `ast.parse` 默认解析 Module，可能需要先解析为 Module 再取 body。
        *   如果 `suite` 为空，使用 `[ast.Expr(value=ast.Constant(value=...))]`.
    3.  **Returns**: `func_spec.return_annotation` -> 调用 `type_builder.build_type_annotation`.
    4.  **Decorators**: `func_spec.decorators` -> 解析.
    5.  Return `ast.FunctionDef` (目前暂不支持 async 定义在 Spec 中，虽然 Spec 有 `AsyncFunctionDef` 的解析逻辑，但 create 暂时只支持同步。若需支持 async，需在 `FunctionSpec` 增加 `is_async` 字段，构建时选择 `ast.AsyncFunctionDef`).

### 3.4 `function_builder.build_parameter` & `build_parameter_as_attribute`

*   **`build_parameter` (Function Arg)**:
    *   **Input**: `param_spec: ParameterSpec`
    *   **Output**: `ast.arg`
    *   **Logic**:
        *   `annotation` -> `type_builder.build_type_annotation`.
        *   Return `ast.arg(arg=param_spec.name, annotation=annotation)`.
        *   **Note**: `ast.arguments` 中 defaults 列表需单独构建并对齐。

*   **`build_parameter_as_attribute` (Class Attr)**:
    *   **Input**: `param_spec: ParameterSpec`
    *   **Output**: `ast.AnnAssign`
    *   **Logic**:
        *   `target` = `ast.Name(id=param_spec.name)`.
        *   `annotation` -> `type_builder.build_type_annotation`.
        *   `value`: 如果 `param_spec.default` 存在，调用 `param_spec.default.render()` 得到的字符串解析为 AST expression (或者 `FieldSpec` 将来也支持 build AST)。目前 `FieldSpec` 只有 render，可以先用 `ast.parse(expr, mode='eval').body`.
        *   Return `ast.AnnAssign`.

### 3.5 `type_builder.build_type_annotation`

*   **Input**: `type_spec: TypeAnnotationSpec`
*   **Output**: `ast.expr`
*   **Logic**:
    1.  如果 `type_spec.args` 为空: return `ast.Name(id=type_spec.name)`.
    2.  如果 `type_spec.name == "Union"`:
        *   递归构建 args。
        *   使用 `ast.BinOp(left=..., op=ast.BitOr(), right=...)` 串联 (Python 3.10+ style).
    3.  Generic (e.g., `List[...]`):
        *   `value` = `ast.Name(id=type_spec.name)`.
        *   `slice`:
            *   如果 `len(args) == 1`: `build_type_annotation(args[0])`.
            *   否则: `ast.Tuple(elts=[...])`.
        *   Return `ast.Subscript`.

### 3.6 `import_builder.build_import`

*   **Input**: `import_spec: ImportFromSpec`
*   **Output**: `ast.Import | ast.ImportFrom`
*   **Logic**:
    *   如果 `module == "__root__"`:
        *   Return `ast.Import(names=[ast.alias(name=n.name, asname=n.alias) for n in names])`.
    *   否则:
        *   Return `ast.ImportFrom(module=module, names=[ast.alias(name=n.name, asname=n.alias) for n in names], level=0)`.

---

## 4. AstParsers (AST -> Spec) 详细设计

此部分逻辑主要从 Domain Spec 的 `parse_ast` 方法迁移。

### 4.1 `module_parser.parse_module`

*   **Input**: `node: ast.Module`, `module_name: str`
*   **Output**: `ModuleSpec`
*   **Logic**:
    *   初始化 lists: classes, functions, imports, enums.
    *   遍历 `node.body`:
        *   `ast.ClassDef`:
            *   如果 `module_name == "enums"` (convention) 或 base class 是 `Enum`: 调用 `enum_parser.parse_enum`.
            *   否则: 调用 `class_parser.parse_class`.
        *   `ast.FunctionDef`, `ast.AsyncFunctionDef`: 调用 `function_parser.parse_function`.
        *   `ast.Import`, `ast.ImportFrom`: 调用 `import_parser.parse_import`.
    *   Return `ModuleSpec.create(...)`.

### 4.2 `class_parser.parse_class`

*   **Input**: `node: ast.ClassDef`
*   **Output**: `ClassSpec`
*   **Logic**:
    *   `inheritance`: `[ast.unparse(b) for b in node.bases]`.
    *   `decorators`: `[ast.unparse(d) for d in node.decorator_list]`.
    *   `description`: `ast.get_docstring(node)`.
    *   `attributes`, `methods`: 遍历 `node.body`:
        *   `ast.FunctionDef/AsyncFunctionDef`: `function_parser.parse_function`.
        *   `ast.AnnAssign`: `function_parser.parse_parameter_from_assign` (Refactored from ParameterSpec).
        *   `ast.Assign`: 同上.
    *   **Pydantic Detection**: 逻辑需保留。`in_pydantic_model = check_bases(inheritance)`. 传递给 `parse_parameter_from_assign`.

### 4.3 `function_parser.parse_function`

*   **Input**: `node: ast.FunctionDef | ast.AsyncFunctionDef`
*   **Output**: `FunctionSpec`
*   **Logic**:
    *   `parameters`: 遍历 `node.args.args`.
        *   `annotation`: Call `type_parser.parse_type(arg.annotation)`.
        *   `ParameterSpec.create(...)`.
    *   `return_annotation`: `type_parser.parse_type(node.returns)`.
    *   `suite`:
        *   如果 `node.body`: `"\n".join([ast.unparse(b) for b in node.body])`.
        *   为空则 `""`.
    *   `decorators`: `unparse`.
    *   `function_type`: 根据 decorators (`classmethod`, `staticmethod`) 和首个参数名 (`self`) 判断。

### 4.4 `type_parser.parse_type`

*   **Input**: `node: ast.AST | None`
*   **Output**: `TypeAnnotationSpec`
*   **Logic**:
    *   (Ref: `TypeAnnotationSpec.parse_ast`)
    *   Recursively handle `Name`, `Constant`, `Subscript` (Generic), `BinOp` (BitOr -> Union), `Attribute`.
    *   Fallback: `ast.unparse(node)`.

*   **New Helper**: `parse_type_str(annotation: str)`
    *   Uses `ast.parse(annotation, mode='eval').body`.
    *   Calls `parse_type(node)`.

### 4.5 `import_parser.parse_import`

*   **Input**: `node: ast.Import | ast.ImportFrom`
*   **Output**: `ImportFromSpec`
*   **Logic**:
    *   Extract module name (`__root__` if `Import`).
    *   Extract names (`ast.alias`).

---

## 5. PythonSyntaxTranslator 重构方案

### 5.1 移除 TemplatePort 依赖

`PythonSyntaxTranslator` 将不再持有 `TemplatePort`，改为持有 `SourceCodePort`。

```python
@dataclass
class PythonSyntaxTranslator:
    source_code_port: SourceCodePort
    file_system_port: FileSystemPort
    # ...
```

### 5.2 重构 `to_package_spec` (反向)

```python
def to_package_spec(self, package_path: Path) -> PackageSpec:
    # ...
    # Old: modules.append(ModuleSpec.parse_code(source_code, filepath.stem))
    # New:
    source_code = self.file_system_port.read_file(filepath)
    modules.append(
        self.source_code_port.parse_module(source_code, filepath.stem)
    )
    # ...
```

### 5.3 重构 `to_code` (正向)

```python
def to_code(self, module_spec: ModuleSpec, imports: Iterable[ImportFromSpec]) -> str:
    # Old: self.template_port.render("module.j2", context)
    # New:
    return self.source_code_port.render_module(module_spec, list(imports))
```

## 6. Domain Spec Cleanup Plan

在 `AstTranslator` 实现并通过测试后，执行以下清理：

1.  **Remove Methods**:
    *   `ModuleSpec.parse_code`
    *   `ClassSpec.parse_ast`
    *   `FunctionSpec.parse_ast`
    *   `ParameterSpec.parse_ast`
    *   `TypeAnnotationSpec.parse_ast`, `TypeAnnotationSpec.parse`, `TypeAnnotationSpec._parse_node`
        *   *Note*: `TypeAnnotationSpec.parse(str)` is used by `ParameterSpec.create`. This dependency needs to be inverted or handled.
        *   **Solution**: `ParameterSpec.create` should probably accept `TypeAnnotationSpec` object primarily. parsing string should be done by a factory service or helper in Infra, OR, keep `parse(str)` but make it NOT rely on `ast`.
        *   **Revised Decision**: `TypeAnnotationSpec` is a Value Object. Using `ast` for parsing strictly structurally is borderline but acceptable if we want to support string input convenient. **HOWEVER**, strictly speaking, it violates the rule.
        *   **Better Approach**: Move `TypeAnnotationSpec.parse(str)` logic to `AstTranslator`. `ParameterSpec.create` assuming string input is convenience that hides parsing complexity.
        *   **Action**: Change `ParameterSpec.create` signature to require `TypeAnnotationSpec`? No, that degrades DX.
        *   **Compromise**: Keep `TypeAnnotationSpec.parse(str)` but implement it via a **simple regex/string parser** for simple cases, or acknowledge that avoiding `ast` entirely for complex types in Domain is hard.
        *   **Strict DDD**: Domain shouldn't know how to parse "List[int]". Infra should.
        *   **Final Plan**:
            *   Remove `parse_ast`.
            *   Keep `parse(str)` but mark it as simplified or move deep parsing to Infrastructure.
            *   Actually, `SourceCodePort` handles full module parsing. Small fragment parsing (like verifying a type string) might belong to a separate helper or stay if we accept `ast` as a "utility" (but User Rule says NO).
            *   **Resolution**: Remove `parse(str)` from `TypeAnnotationSpec`. `ParameterSpec.create` input `annotation` MUST be `TypeAnnotationSpec`. If caller has string, caller uses `AstTranslator` (or a helper) to parse it first. This enforces strict layer separation.

2.  **Remove Imports**:
    *   Delete `import ast` from all spec files.

## 7. Testing Strategy

1.  **Unit Tests (Builders)**:
    *   Spec -> verify AST structure (using `ast.dump` or assert properties).
    *   Spec -> `render_module` -> `compile()` verifying syntax validity.
2.  **Unit Tests (Parsers)**:
    *   Source Code -> `parse_module` -> verify Spec equality.
    *   Reuse current `parse_ast` tests but redirect to `AstTranslator`.
3.  **Round-Trip Tests**:
    *   Spec A -> render -> Code -> parse -> Spec B. Assert A == B.
