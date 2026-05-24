# AST 表达式实现指南

## 工作流程

1. 运行命令触发解析：
   ```bash
   uv run codegen reverse-code code_metadata -n <ComponentName>
   ```

2. 根据报错补充实现，报错格式：
   ```
   NotImplementedError: Unsupported node type: <class 'ast.XXX'>
   ```

3. 重复执行直到不再出现 `AstToExpr` 相关错误

## 实现规范

### 1. 值对象定义

位置：`src/codegen/code_metadata/domain/value_objects/`

```python
from dataclasses import dataclass
from codegen.code_metadata.domain.core.ast_expr import AstExpr

@dataclass
class AstXxx(AstExpr):
    """Represents an ast.Xxx node."""
    # 属性与 ast.Xxx 保持一致
    attr: type
```

### 2. Mapper 方法

位置：`src/codegen/code_metadata/infrastructure/mappers/ast_to_expr.py`

每个节点类型一个独立方法：

```python
class AstToExpr:

    @staticmethod
    def to_expr(node: ast.expr | None) -> AstExpr | None:
        if node is None:
            return None
        match node:
            case ast.Xxx():
                return AstToExpr.to_ast_xxx(node)
            case _:
                raise NotImplementedError(f"Unsupported node type: {type(node)}")

    @staticmethod
    def to_ast_xxx(node: ast.Xxx) -> AstXxx:
        return AstXxx(attr=node.attr)
```

## 已实现的节点类型

| AST 节点 | 值对象 | 说明 |
|---------|--------|------|
| `ast.Name` | `AstName` | 变量/标识符引用 |
| `ast.Call` | `AstCall` | 函数/类实例化调用 |
