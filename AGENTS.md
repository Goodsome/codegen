# AGENTS.md - Codegen 项目开发指南

本文档为 AI 编码代理提供项目开发规范和命令参考。

## 项目概述

- **项目名称**: Codegen
- **project_id**: Codegen
- **项目描述**: DDD（领域驱动设计）代码生成工具，从 `codegen.yaml` 蓝图文件生成 Python 代码

## 构建与测试命令

### 依赖管理

```bash
# 安装依赖（使用 uv）
uv sync

# 安装项目为可编辑模式
uv tool install -e --python 3.13 .
```

### 测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/unit/python_gen/infrastructure/adapters/test_ast_translator.py

# 运行单个测试函数
pytest tests/unit/python_gen/infrastructure/adapters/test_ast_translator.py::TestAstTranslatorBuilders::test_render_simple_module

# 运行特定目录的测试
pytest tests/unit/
pytest tests/e2e/

# 显示详细输出
pytest -v

# 显示 print 输出
pytest -s
```

### 代码质量检查

```bash
# 代码格式化
black src/ tests/

# Lint 检查
ruff check src/ tests/

# 类型检查
basedpyright src/
# 或
pyrefly check src/
```

### CLI 命令

```bash
# 从蓝图生成代码
codegen build

# 查看蓝图结构树
codegen tree

# 获取蓝图值
codegen get <path>

# 设置蓝图值
codegen set <path> <value>

# 删除蓝图值
codegen rm <path>
```

## 项目结构

```
src/codegen/
├── domain_definition/      # 领域定义模块（解析 blueprint）
│   ├── domain/             # 领域层：值对象、实体、端口
│   ├── application/        # 应用层：用例
│   └── infrastructure/     # 基础设施层：适配器
├── python_gen/             # Python 代码生成模块
│   ├── domain/             # 领域层
│   ├── application/        # 应用层
│   └── infrastructure/     # 基础设施层
├── orchestration/          # 编排层
├── shared/                 # 共享模块
└── entrypoints/            # 入口点（CLI、MCP）
```

## 代码风格规范

### 导入顺序

1. 标准库（如 `ast`, `dataclasses`, `pathlib`）
2. 第三方库（如 `pydantic`, `typer`）
3. 本地模块（`from codegen.xxx import xxx`）

示例：
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, Field

from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
```

### 类型注解

- 使用 Python 3.13+ 类型语法（如 `list[str]` 而非 `List[str]`）
- 使用 `|` 表示联合类型（如 `str | None` 而非 `Optional[str]`）
- 公共方法必须有类型注解

```python
def render_module(self, module_spec: ModuleSpec, imports: list[ImportFromSpec]) -> str:
    ...

def parse_module(self, source_code: str, module_name: str) -> ModuleSpec:
    ...
```

### 命名约定

| 类型     | 命名风格                  | 示例                                 |
|--------|-----------------------|------------------------------------|
| 类名     | PascalCase            | `ModuleSpec`, `AstTranslator`      |
| 函数/方法  | snake_case            | `render_module`, `parse_module`    |
| 变量     | snake_case            | `module_spec`, `source_code`       |
| 常量     | UPPER_SNAKE           | `MAX_RETRIES`                      |
| 私有属性   | `_leading_underscore` | `_domain_events`                   |
| 端口（接口） | XxxPort               | `SourceCodePort`, `FileSystemPort` |
| 适配器    | XxxAdapter 或 Xxx      | `JinjaAdapter`, `AstTranslator`    |
| 用例     | Xxx / XxxUseCase      | `LoadBlueprint`, `GeneratePackage` |
| 值对象    | XxxSpec / XxxVO       | `ModuleSpec`, `PascalString`       |

### DDD 架构分层

**领域层 (domain/)**
- 值对象：继承 `ValueObject`，不可变（`frozen=True`）
- 实体：继承 `Entity`，有唯一标识
- 端口：定义接口（Protocol 或抽象类）
- 服务：无状态的领域服务

**应用层 (application/)**
- 用例：编排领域对象，执行业务逻辑
- 命令/查询对象：参数封装

**基础设施层 (infrastructure/)**
- 适配器：实现端口接口
- 外部服务集成

**入口点 (entrypoints/)**
- CLI 命令
- MCP 服务
- HTTP API（如有）

### Pydantic 模型规范

```python
from pydantic import BaseModel, ConfigDict, Field

class ValueObject(BaseModel):
    """值对象：不可变、禁止额外字段"""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

class MySpec(ValueObject):
    name: str
    items: list[str] = Field(default_factory=list)
```

### 错误处理

- 领域层：抛出明确的异常类型
- 应用层：捕获并转换异常
- 基础设施层：处理外部错误

```python
# 领域层验证
if not self.file_system_port.is_directory(package_path):
    raise ValueError(f"Expected a directory, got {package_path}")

# 解析错误
with pytest.raises(SyntaxError):
    translator.parse_module(invalid_code, "test_mod")
```

### 文档字符串

- 使用三引号文档字符串
- 简洁描述功能
- 可选：Args/Returns 说明

```python
def render_module(self, module_spec: ModuleSpec, imports: list[ImportFromSpec]) -> str:
    """
    Renders a ModuleSpec into Python source code string.
    """
    ...
```

### 依赖注入

使用 `dependency-injector` 库：

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    my_service = providers.Singleton(
        MyService,
        dependency=other_provider,
    )
```

### 测试规范

- 测试文件命名：`test_<module_name>.py`
- 测试类命名：`Test<FeatureName>`
- 测试方法命名：`test_<scenario>`
- 使用 pytest fixtures 共享测试数据

```python
class TestAstTranslatorBuilders:
    """Unit tests for Spec -> AST builders."""

    def test_render_simple_module(self):
        translator = AstTranslator()
        module_spec = ModuleSpec.create(name="test_mod")
        source_code = translator.render_module(module_spec, [])
        assert isinstance(source_code, str)
```

## 重要文件

- `codegen.yaml` - 项目蓝图定义
- `conftest.py` - pytest 共享配置和 fixtures
- `src/codegen/bootstrap.py` - 依赖注入容器配置

## 注意事项

1. **不要添加注释** - 除非用户明确要求
2. **遵循现有代码风格** - 查看相邻文件了解惯例
3. **保持 DDD 分层** - 不要跨层直接调用
4. **使用类型安全的字符串** - `SnakeString`, `PascalString` 等
5. **测试覆盖率** - 新增功能需要对应测试
