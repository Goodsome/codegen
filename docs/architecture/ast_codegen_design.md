# ADR: AST-Based Python Code Generation

> **Status**: Proposed
> **Date**: 2026-02-17
> **Ref**: docs/stories/S260217_AST_Based_Codegen.md

## 1. Context (背景)

当前代码生成系统存在两个层面的架构问题：

### 1.1 正向生成：Jinja2 模板的脆弱性

代码生成依赖 Jinja2 模板 (`python_gen/templates/*.j2`) 将 PythonGen 领域的 Spec 对象转换为 Python 源代码。存在以下问题：

1. **缩进脆弱性**: Jinja2 模板中的缩进控制 (`{% filter indent(width=4) %}`) 容易出错，嵌套层级深时尤其困难。
2. **语法安全性缺失**: 模板生成的字符串无法保证是合法的 Python 语法，错误只能在运行时才被发现。
3. **可维护性差**: 模板中混合了控制流和输出格式，对复杂场景（如条件装饰器、多重继承）的支持不够灵活。

### 1.2 反向解析：Domain 层违规依赖 `ast` 模块

当前多个 Domain 层的 Spec 对象直接依赖 Python `ast` 模块进行反向解析（从源码重建 Spec），违反了 **"Domain objects must NOT depend on the `ast` module"** 的约束：

| Spec 对象              | 违规方法                        | 依赖的 ast 类型                          |
| ---------------------- | ------------------------------- | --------------------------------------- |
| `ModuleSpec`           | `parse_code(source_code, name)` | `ast.parse()`, `ast.ClassDef` 等        |
| `ClassSpec`            | `parse_ast(node, source_code)`  | `ast.ClassDef`, `ast.unparse()`         |
| `FunctionSpec`         | `parse_ast(node, source_code)`  | `ast.FunctionDef`, `ast.unparse()`      |
| `ParameterSpec`        | `parse_ast(node)`               | `ast.AnnAssign`, `ast.Assign`           |
| `TypeAnnotationSpec`   | `parse_ast(node)`, `parse(str)` | `ast.parse()`, `ast.Name` 等递归结构     |
| `PythonEnumSpec`       | `parse_ast(node)`               | `ast.ClassDef`, `ast.unparse()`         |
| `PythonEnumMemberSpec` | `parse_ast(node)`               | `ast.Assign`, `ast.AnnAssign`           |
| `ImportFromSpec`       | `parse_ast(node)`               | `ast.Import`, `ast.ImportFrom`          |

此外，`PythonSyntaxTranslator`（Domain Service）的 `to_package_spec()` 方法调用了这些 `parse_ast` 方法，整个反向解析链路都在 Domain 层内完成，与 `ast` 模块紧密耦合。

### 1.3 解决方向

Python 标准库提供了 `ast` 模块，允许我们以编程方式构建语法树并通过 `ast.unparse()` (Python 3.9+) 生成源代码。AST 方式能**天然保证语法正确性**，并且**自动处理缩进**。

我们应当利用这次重构，**同时解决正向生成和反向解析两个方向的 `ast` 依赖**，将所有 AST 相关逻辑统一收敛到 Infrastructure 层。

## 2. Decision (决策)

### 2.1 核心策略：引入双向 AstTranslator (Infrastructure Adapter)

在 `PythonGen` 上下文的 Infrastructure 层新增 `AstTranslator`，**同时**承担：
- **正向生成**: Spec → `ast.AST` → `ast.unparse()` → Python 源代码（替代 Jinja2 模板）
- **反向解析**: Python 源代码 → `ast.parse()` → Spec 对象（替代 Domain 层的 `parse_ast` 方法）

```
┌──────────────────────────────────────────────────────────────────┐
│                       PythonGen Context                         │
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────────────┐  │
│  │ Domain (Pure)        │      │ Application                  │  │
│  │                      │      │                              │  │
│  │ ModuleSpec           │      │  GeneratePackage (use case)  │  │
│  │ ClassSpec            │─────▶│  ParsePackage    (use case)  │  │
│  │ FunctionSpec         │      │                              │  │
│  │ ...                  │      │  PythonSyntaxTranslator      │  │
│  │                      │      │  (domain service)            │  │
│  │ ⚠️ 不再包含 parse_ast │      └──────────────┬───────────────┘  │
│  │ ⚠️ 不再 import ast    │                     │                 │
│  └──────────────────────┘                      │                 │
│                                                │                 │
│  ┌─────────────────────────────────────────────▼──────────────┐  │
│  │ Infrastructure                                             │  │
│  │                                                            │  │
│  │  ┌────────────────────┐    ┌────────────────────────────┐  │  │
│  │  │ JinjaSourceCode    │    │ AstTranslator [NEW]        │  │  │
│  │  │ Adapter (兼容层)    │    │ (implements SourceCodePort)│  │  │
│  │  │                    │    │                            │  │  │
│  │  │ render_module() ✅  │    │ render_module()  (正向) ✅  │  │  │
│  │  │ parse_module()  ❌  │    │ parse_module()   (反向) ✅  │  │  │
│  │  └────────────────────┘    └────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 不复用 TemplatePort，新增 SourceCodePort

**原因分析**：

现有 `TemplatePort` 的接口签名为：
```python
class TemplatePort(ABC):
    @abstractmethod
    def render(self, template_path: str, context: Dict[str, Any]) -> str: ...
```

这个接口假设了「基于模板文件路径 + 上下文字典」的渲染模型。AST 方式并不需要模板文件，也不使用通用字典上下文。因此 **不应强行适配**，而应引入一个语义更精确的新 Port。

同时，反向解析（`parse_ast`）目前散布在各个 Domain Spec 对象中，也违反了分层原则。新 Port 应当是**双向的**，统一封装正向生成和反向解析。

**新 Port 定义** (位于 `python_gen/domain/ports/`):

```python
from abc import ABC, abstractmethod
from pathlib import Path
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec


class SourceCodePort(ABC):
    """Port for bidirectional translation between Spec objects and Python source code.
    
    正向 (Spec → Code): render_module
    反向 (Code → Spec): parse_module
    """

    @abstractmethod
    def render_module(
        self,
        module_spec: ModuleSpec,
        imports: list[ImportFromSpec],
    ) -> str:
        """
        将一个 ModuleSpec 及其所需的导入转换为完整的 Python 源代码字符串。
        """
        ...

    @abstractmethod
    def parse_module(
        self,
        source_code: str,
        module_name: str,
    ) -> ModuleSpec:
        """
        将 Python 源代码字符串解析为 ModuleSpec。
        反向解析逻辑 (ast.parse → Spec) 由 Infrastructure 实现。
        """
        ...
```

### 2.3 为什么 AST 逻辑不能留在 Domain 层？

关键设计约束来自 User Story：**Domain objects must NOT depend on the `ast` module**。

`ast` 模块属于 Python 平台特定的技术细节。虽然当前项目只生成 Python 代码，但将 AST 相关逻辑（无论是正向生成还是反向解析）放置在 Infrastructure 层更符合 DDD 的分层原则：

- **Domain 层** 知道「是什么」(Spec 对象的结构与语义)
- **Infrastructure 层** 知道「怎么做」（怎么从源码构建 Spec、怎么从 Spec 生成源码）

当前 Domain 层的 `parse_ast` 方法本质上是 **反序列化逻辑**，与 Spec 对象的领域语义无关。正如我们不会在 Domain Entity 上放置 `from_json()` 或 `from_database_row()` 方法一样，`parse_ast(ast.ClassDef)` 也不应出现在 Domain 的 `ClassSpec` 上。

这使得将来如果需要支持其他代码分析后端（如 RedBaron, libCST, tree-sitter），只需新增 Adapter 即可。

## 3. Spec → AST 映射策略 (Mapping Strategy)

### 3.1 映射总表

下表定义了每个 Spec 对象到 `ast.AST` 节点的映射关系：

| Spec Object          | Target AST Node(s)                      | 备注                                       |
| --------------------- | ---------------------------------------- | ------------------------------------------ |
| `ModuleSpec`          | `ast.Module`                             | 顶层容器，包含 imports + classes + functions + enums |
| `ImportFromSpec`      | `ast.ImportFrom` / `ast.Import`          | 根据 module 是否为 `__root__` 判断               |
| `ClassSpec`           | `ast.ClassDef`                           | 含 decorators, bases, body                  |
| `FunctionSpec`        | `ast.FunctionDef` / `ast.AsyncFunctionDef` | 根据 function_type 判断是否需要 self            |
| `ParameterSpec`       | `ast.arg` (in `ast.arguments`)           | 带 annotation                               |
| `TypeAnnotationSpec`  | `ast.Name` / `ast.Subscript` / `ast.BinOp` | 递归构建                                     |
| `PythonEnumSpec`      | `ast.ClassDef`                           | body 为 `ast.Assign`                        |
| `PythonEnumMemberSpec`| `ast.Assign`                             | target + value                              |
| `FieldSpec`           | `ast.Call` (Field(...) / field(...))     | 作为属性的 default value                      |
| `ImportedName`        | `ast.alias`                              | name + asname                               |

### 3.2 核心映射伪代码

#### 3.2.1 ModuleSpec → ast.Module

```python
def translate_module(module_spec: ModuleSpec, imports: list[ImportFromSpec]) -> ast.Module:
    body: list[ast.stmt] = []
    
    # 1. 构建 import 语句
    for imp in imports:
        body.append(translate_import(imp))
    
    # 2. 构建 enum 定义
    for enum in module_spec.enums:
        body.append(translate_enum(enum))
    
    # 3. 构建 class 定义
    for cls in module_spec.classes:
        body.append(translate_class(cls))
    
    # 4. 构建 function 定义
    for func in module_spec.functions:
        body.append(translate_function(func))
    
    module = ast.Module(body=body, type_ignores=[])
    ast.fix_missing_locations(module)
    return module
```

#### 3.2.2 ClassSpec → ast.ClassDef

```python
def translate_class(class_spec: ClassSpec) -> ast.ClassDef:
    body: list[ast.stmt] = []
    
    # Docstring
    if class_spec.description:
        body.append(ast.Expr(value=ast.Constant(value=class_spec.description)))
    
    # Attributes (as AnnAssign)
    for attr in class_spec.attributes:
        body.append(translate_parameter_as_attribute(attr))
    
    # Methods
    for method in class_spec.methods:
        body.append(translate_function(method))
    
    # Empty class body
    if not body:
        body.append(ast.Expr(value=ast.Constant(value=...)))
    
    return ast.ClassDef(
        name=str(class_spec.name),
        bases=[ast.parse(b, mode='eval').body for b in class_spec.inheritance],
        keywords=[],
        body=body,
        decorator_list=[ast.parse(d, mode='eval').body for d in class_spec.decorators],
    )
```

#### 3.2.3 FunctionSpec → ast.FunctionDef

```python
def translate_function(func_spec: FunctionSpec) -> ast.FunctionDef | ast.AsyncFunctionDef:
    # 构建参数列表
    args_list: list[ast.arg] = []
    
    # Instance methods need 'self'
    if func_spec.is_instance_method():
        args_list.append(ast.arg(arg='self'))
    
    for param in func_spec.parameters:
        args_list.append(translate_parameter(param))
    
    arguments = ast.arguments(
        posonlyargs=[],
        args=args_list,
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],  # TODO: handle defaults
    )
    
    # 构建函数体
    if func_spec.suite:
        body = ast.parse(func_spec.suite).body
    else:
        body = [ast.Expr(value=ast.Constant(value=...))]
    
    # Return annotation
    returns = translate_type_annotation(func_spec.return_annotation)
    
    # decorators
    decorator_list = [ast.parse(d, mode='eval').body for d in func_spec.decorators]
    
    node_cls = ast.FunctionDef  # TODO: 未来可能支持 AsyncFunctionDef
    
    return node_cls(
        name=str(func_spec.name),
        args=arguments,
        body=body,
        decorator_list=decorator_list,
        returns=returns,
    )
```

#### 3.2.4 TypeAnnotationSpec → ast.expr

```python
def translate_type_annotation(spec: TypeAnnotationSpec) -> ast.expr:
    if not spec.args:
        return ast.Name(id=spec.name, ctx=ast.Load())
    
    if spec.name == 'Union':
        # Python 3.10+ Union syntax: X | Y
        result = translate_type_annotation(spec.args[0])
        for arg in spec.args[1:]:
            result = ast.BinOp(
                left=result,
                op=ast.BitOr(),
                right=translate_type_annotation(arg),
            )
        return result
    
    # Generic: Container[Args]
    return ast.Subscript(
        value=ast.Name(id=spec.name, ctx=ast.Load()),
        slice=_build_slice(spec.args),
        ctx=ast.Load(),
    )

def _build_slice(args: list[TypeAnnotationSpec]) -> ast.expr:
    if len(args) == 1:
        return translate_type_annotation(args[0])
    return ast.Tuple(
        elts=[translate_type_annotation(a) for a in args],
        ctx=ast.Load(),
    )
```

### 3.3 AstTranslator 的内部组织

`AstTranslator` 本身是一个 Infrastructure Adapter，实现 `SourceCodePort` 的双向接口。内部应按「职责单一」原则拆分为 Builder (正向) 和 Parser (反向) 两组模块：

```
python_gen/infrastructure/adapters/
├── ast_translator.py              # 入口：实现 SourceCodePort (双向)
├── ast_builders/                  # 正向：Spec → ast.AST（不导出）
│   ├── __init__.py
│   ├── module_builder.py          # ModuleSpec → ast.Module
│   ├── class_builder.py           # ClassSpec → ast.ClassDef
│   ├── function_builder.py        # FunctionSpec → ast.FunctionDef
│   ├── enum_builder.py            # PythonEnumSpec → ast.ClassDef
│   ├── import_builder.py          # ImportFromSpec → ast.Import/ImportFrom
│   └── type_builder.py            # TypeAnnotationSpec → ast.expr
└── ast_parsers/                   # 反向：ast.AST → Spec（不导出）
    ├── __init__.py
    ├── module_parser.py           # ast.Module → ModuleSpec
    ├── class_parser.py            # ast.ClassDef → ClassSpec
    ├── function_parser.py         # ast.FunctionDef → FunctionSpec
    ├── enum_parser.py             # ast.ClassDef → PythonEnumSpec
    ├── import_parser.py           # ast.Import/ImportFrom → ImportFromSpec
    └── type_parser.py             # ast.expr → TypeAnnotationSpec
```

- **Builder** 是纯函数模块，接收 Spec 对象，返回 `ast.AST` 节点。
- **Parser** 是纯函数模块，接收 `ast.AST` 节点，返回 Spec 对象。本质上是将当前散布在各 Spec 上的 `parse_ast` 方法的逻辑**平移到 Infrastructure 层**。
- `AstTranslator` 负责组合这些模块，统一对外提供 `render_module()` 和 `parse_module()` 两个方法。

## 4. 对现有模型的影响评估 (Impact Assessment)

### 4.1 PythonGen Domain — 需要重构 (移除 `ast` 依赖)

**结论：Domain 层 Spec 对象需要移除所有 `parse_ast` / `parse_code` 类方法及其对 `ast` 模块的 `import`。**

#### 4.1.1 正向生成所需的信息 — 已完备

当前 Spec 对象已经具备了 AST 构建所需的全部信息（这些纯数据属性不受影响）：

| 信息需求             | 现有 Spec 支持  | 备注                  |
| -------------------- | -------------- | --------------------- |
| 类名、基类、装饰器   | `ClassSpec`     | ✅ 完整               |
| 方法签名、参数、返回值 | `FunctionSpec`  | ✅ 完整               |
| 参数名、类型注解、默认值 | `ParameterSpec` | ✅ 完整              |
| 类型注解递归结构      | `TypeAnnotationSpec` | ✅ 完整          |
| 导入语句             | `ImportFromSpec` | ✅ 完整              |
| 枚举定义             | `PythonEnumSpec` | ✅ 完整              |
| 函数体               | `FunctionSpec.suite` | ✅ 字符串形式，可通过 `ast.parse()` 还原 |

#### 4.1.2 反向解析方法 — 需迁移到 Infrastructure

以下方法需从 Domain Spec 对象上**移除**，其逻辑迁移到 `ast_parsers/` 模块：

| Spec 对象              | 待移除方法                        | 迁移目标                       |
| ---------------------- | -------------------------------- | ------------------------------ |
| `ModuleSpec`           | `parse_code(source_code, name)`  | `ast_parsers/module_parser.py` |
| `ClassSpec`            | `parse_ast(node, source_code)`   | `ast_parsers/class_parser.py`  |
| `FunctionSpec`         | `parse_ast(node, source_code)`   | `ast_parsers/function_parser.py` |
| `ParameterSpec`        | `parse_ast(node)`                | `ast_parsers/function_parser.py` (内部) |
| `TypeAnnotationSpec`   | `parse_ast(node)`, `parse(str)`  | `ast_parsers/type_parser.py`   |
| `PythonEnumSpec`       | `parse_ast(node)`                | `ast_parsers/enum_parser.py`   |
| `PythonEnumMemberSpec` | `parse_ast(node)`                | `ast_parsers/enum_parser.py` (内部) |
| `ImportFromSpec`       | `parse_ast(node)`                | `ast_parsers/import_parser.py` |

迁移后，这些 Spec 对象将成为**纯数据对象**（仅包含 `create()` 工厂方法、领域行为方法如 `merge()`/`get_required_types()` 等），彻底消除对 `ast` 模块的 import。

> **注意**：`TypeAnnotationSpec.parse(str)` 方法内部也使用了 `ast.parse(annotation, mode="eval")`，同样需要迁移。但 `TypeAnnotationSpec.render() -> str` 方法是纯字符串拼接，不依赖 `ast`，可以保留在 Domain 层。
> 
> **注意**：`ImportFromSpec.render()` 方法也是纯字符串拼接，不依赖 `ast`，保留在 Domain 层。

### 4.2 PythonSyntaxTranslator — 需全面重构

当前 `PythonSyntaxTranslator` 是 **Domain Service**，同时承担了两个职责，**两个方向都需要重构**：

1. **反向解析** (`to_package_spec`): 从 Python 源码重建 Spec 对象
   - 当前调用 `ModuleSpec.parse_code()` → 间接依赖 `ast` 模块 ← ⚠️ **需重构**
2. **正向生成** (`to_code`, `generate_source_tree`): 将 Spec 生成 Python 源码
   - 当前依赖 `TemplatePort` (Jinja2) ← ⚠️ **需重构**

#### 重构方案

将 `PythonSyntaxTranslator` 的**双向**职责都委托给 `SourceCodePort`：

**Before:**
```python
@dataclass
class PythonSyntaxTranslator:
    template_port: TemplatePort        # Jinja2 依赖
    file_system_port: FileSystemPort

    def to_package_spec(self, package_path: Path) -> PackageSpec:
        # ... 调用 ModuleSpec.parse_code() → 使用 ast 模块
        source_code = self.file_system_port.read_file(filepath)
        modules.append(ModuleSpec.parse_code(source_code, filepath.stem))

    def to_code(self, module_spec, imports) -> str:
        context = {"module_spec": module_spec, "imports": imports}
        return self.template_port.render("module.j2", context)
```

**After:**
```python
@dataclass
class PythonSyntaxTranslator:
    source_code_port: SourceCodePort   # 双向抽象 Port (替代 TemplatePort)
    file_system_port: FileSystemPort

    def to_package_spec(self, package_path: Path) -> PackageSpec:
        # ... 反向解析委托给 SourceCodePort
        source_code = self.file_system_port.read_file(filepath)
        modules.append(self.source_code_port.parse_module(source_code, filepath.stem))

    def to_code(self, module_spec, imports) -> str:
        # ... 正向生成委托给 SourceCodePort
        return self.source_code_port.render_module(module_spec, imports)
```

这样 `PythonSyntaxTranslator` 不再依赖 `TemplatePort`，也不再间接依赖 `ast` 模块，而是完全通过 `SourceCodePort` 抽象与 Infrastructure 层交互。

### 4.3 GeneratePackage Use Case — 无需修改

`GeneratePackage` 依赖 `PythonSyntaxTranslator`，而不是直接依赖模板端口。只要 `PythonSyntaxTranslator` 的公共接口保持不变，Use Case 层无需任何调整。

### 4.4 Shared Context — 可选保留

`TemplatePort` 和 `JinjaAdapter` 可以保留在 Shared 上下文中，因为其他场景（如 Bootstrap 代码生成）可能仍然需要模板渲染能力。PythonGen 上下文不再直接依赖它们。

### 4.5 CodeFormatter — 保留

`ast.unparse()` 生成的代码虽然语法正确，但格式不够美观（例如缺少空行、紧凑的参数排列）。因此 `BlackCodeFormatter` 作为后处理步骤仍然有存在的意义。流程变为：

```
Spec → ast.Module → ast.unparse() → Black format → Final Code
```

## 5. 迁移策略 (Migration Strategy)

### 5.1 Strangler Fig Pattern (绞杀者模式)

采用渐进式迁移，不做 Big Bang 替换：

```
Phase 0: 引入 SourceCodePort (双向接口) + AstTranslator 骨架
Phase 1: 实现 AstTranslator.parse_module()（反向解析，从 Spec parse_ast 平移逻辑）
Phase 2: 实现 AstTranslator.render_module()（正向生成，替代 Jinja2）
Phase 3: 重构 PythonSyntaxTranslator，依赖切换到 SourceCodePort
Phase 4: 移除 Domain Spec 对象上的 parse_ast 方法和 import ast
Phase 5: 验证所有 E2E 测试通过
Phase 6: 移除 Jinja2 模板文件和 TemplatePort 从 PythonGen 的依赖中
```

### 5.2 JinjaSourceCodeAdapter (兼容层)

为实现平滑过渡，可将现有 Jinja 逻辑包装为 `SourceCodePort` 的实现。注意：此兼容层**仅支持正向生成**，反向解析必须直接使用 `AstTranslator`：

```python
class JinjaSourceCodeAdapter(SourceCodePort):
    """兼容层：使用现有 Jinja2 模板实现 SourceCodePort 的正向生成。"""
    
    def __init__(self, template_port: TemplatePort):
        self._template_port = template_port
    
    def render_module(self, module_spec, imports) -> str:
        context = {"module_spec": module_spec, "imports": imports}
        return self._template_port.render("module.j2", context)
    
    def parse_module(self, source_code, module_name) -> ModuleSpec:
        # Jinja 无法反向解析，此方法需依赖 AST 实现
        raise NotImplementedError(
            "JinjaSourceCodeAdapter does not support reverse parsing. "
            "Use AstTranslator instead."
        )
```

这意味着在迁移期间，`parse_module` 必须先由 `AstTranslator` 实现完成（Phase 1），之后才能移除 Domain 层的 `parse_ast` 方法（Phase 4）。这样 `PythonSyntaxTranslator` 可以先统一到 `SourceCodePort` 接口，再逐步将后端切换为 `AstTranslator`。

## 6. 风险与缓解措施

| 风险                                    | 概率 | 影响 | 缓解措施                                     |
| --------------------------------------- | ---- | ---- | -------------------------------------------- |
| ast.unparse() 输出格式与 Jinja 不一致      | 高   | 低   | 依赖 Black formatter 统一格式；E2E 测试验证      |
| 复杂 suite 字符串解析失败                   | 中   | 中   | suite 已是合法 Python 代码，`ast.parse()` 可安全还原 |
| Domain Spec 信息不足以构建 AST             | 低   | 高   | 上文分析已确认所有信息充足                        |
| 向后兼容性断裂                             | 中   | 高   | Strangler Fig + JinjaSourceCodeAdapter 兼容层    |
| parse_ast 迁移过程中 Domain 行为回归        | 中   | 高   | Parser 用相同测试用例做往返验证；迁移前后对比       |
| Domain Spec 上存在依赖 parse_ast 的调用链   | 中   | 中   | 全项目 grep `parse_ast`/`parse_code`，逐一替换    |

## 7. 实施路线图 (Roadmap)

### T2 — Feature: SourceCodePort 接口设计与 AST 双向映射详细设计
- **产出**: `docs/design/ast_codegen_spec.md`
- **内容**: 
  - `SourceCodePort` 完整双向接口定义
  - 各 Builder (正向) 的详细输入/输出 Schema
  - 各 Parser (反向) 的详细输入/输出 Schema — 从现有 `parse_ast` 逻辑梳理
  - Edge cases 处理策略 (如 `__init__` 模块、空类体、multiline strings)
  - `PythonSyntaxTranslator` 的全面重构方案细节
  - Domain Spec 对象 `parse_ast` 移除计划

### T3 Phase 1 — Scaffolding (骨架构建)
- **产出**: 更新 `codegen.yaml`，生成 `SourceCodePort`、`AstTranslator` 骨架代码
- **范围**: `python_gen/domain/ports/source_code_port.py`, `python_gen/infrastructure/adapters/ast_translator.py`, `python_gen/infrastructure/adapters/ast_builders/`, `python_gen/infrastructure/adapters/ast_parsers/`

### T3 Phase 2 — Test Generation (测试先行)
- **产出**: `tests/python_gen/test_ast_translator.py`
- **策略**: 
  - 正向测试：Spec → render_module → source code → 验证语法正确性
  - 反向测试：source code → parse_module → Spec → 验证结构正确性
  - 往返测试：Spec → render → parse → Spec 对比一致性

### T3 Phase 3 — Logic Implementation (逻辑填充)
- **产出**: ast_builders/ + ast_parsers/ 的完整实现 + `PythonSyntaxTranslator` 全面重构
- **目标**: 所有测试 Green

### T3 Phase 4 — Domain Cleanup (领域净化)
- **产出**: 移除 Domain Spec 对象上所有 `parse_ast` / `parse_code` 方法，移除 `import ast`
- **目标**: Domain 层零 `ast` 依赖

### T3 Phase 5 — Migration & Cleanup
- **产出**: 切换默认实现为 AST，移除 PythonGen 对 Jinja2 模板的依赖

## 8. Decision Record Summary

| 决策点                 | 决策结果                                         |
| ---------------------- | ----------------------------------------------- |
| AST 逻辑放置层          | Infrastructure (Adapter)，包括正向生成和反向解析    |
| Port 接口              | 新增 `SourceCodePort` (双向)，不复用 `TemplatePort` |
| 内部组织               | Builder (正向) + Parser (反向) 双模块组           |
| Domain 层影响          | **需重构**：移除所有 `parse_ast` 方法和 `import ast` |
| PythonSyntaxTranslator | 双向职责都委托给 SourceCodePort                    |
| 迁移策略               | Strangler Fig + JinjaSourceCodeAdapter 兼容层     |
| CodeFormatter          | 保留 (Black 后处理)                              |
