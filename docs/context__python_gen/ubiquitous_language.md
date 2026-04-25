---
name: PythonGen 通用语言与规约
description: PythonGen 上下文内的名词解释、实体不变量与业务约束
type: project
---

# 📖 PythonGen 通用语言与规约

## 🔤 核心名词解释

### 1. PackageSpec (包规约)
- **定义**：代表一个完整的 Python 包（目录）
- **业务含义**：是代码生成的顶级单元，包含包内的所有模块、子包以及 __init__.py 文件定义
- **不变量**：
  - 包名称必须符合 Python 包命名规范（snake_case）
  - 包内的模块与子包名称必须唯一
  - 支持递归嵌套的子包结构

### 2. ModuleSpec (模块规约)
- **定义**：代表一个完整的 Python 模块（.py 文件）
- **业务含义**：是代码生成的基本单元，包含模块内的所有类、函数、导入语句、顶级赋值等元素
- **不变量**：
  - 模块名称必须符合 Python 模块命名规范（snake_case）
  - 模块内的顶级元素名称必须唯一
  - 导入语句必须符合 Python 导入规范

### 3. ClassSpec (类规约)
- **定义**：代表 Python 中的类定义
- **业务含义**：描述类的名称、继承关系、装饰器、属性、方法等所有结构信息
- **不变量**：
  - 类名称必须符合 PascalCase 命名规范
  - 类内的属性与方法名称必须唯一
  - 继承的父类必须是已定义的有效类型

### 4. FunctionSpec (函数规约)
- **定义**：代表 Python 中的函数或方法定义
- **业务含义**：描述函数的名称、装饰器、参数、返回值类型、函数体等所有结构信息
- **不变量**：
  - 函数名称必须符合 snake_case 命名规范
  - 参数顺序必须符合 Python 规范（位置参数→默认参数→可变参数→关键字参数）
  - 返回值类型必须是有效的 Python 类型注解

### 5. VariableSpec (变量规约)
- **定义**：代表 Python 中的变量定义，包括属性、参数、局部变量等
- **业务含义**：描述变量的名称、类型注解、默认值等信息
- **不变量**：
  - 变量名称必须符合 snake_case 命名规范
  - 类型注解必须是有效的 Python 类型

### 6. TypeAnnotationSpec (类型注解规约)
- **定义**：代表 Python 中的类型注解
- **业务含义**：描述类型的结构，支持泛型、联合类型等复杂类型定义
- **不变量**：
  - 类型名称必须是有效的 Python 类型
  - 泛型参数必须符合类型定义的约束

### 7. RawCodeSpec (原始代码规约)
- **定义**：代表无法被结构化解析的原始代码片段
- **业务含义**：用于保留用户手动编写的、无法映射到领域模型的自定义代码
- **不变量**：
  - 代码内容必须是合法的 Python 语法
  - 不得包含会破坏整个模块语法的片段

### 8. ModuleAssignmentSpec (模块顶级赋值规约)
- **定义**：代表 Python 模块中的顶级赋值语句
- **业务含义**：用于描述模块级别的常量、变量、别名等定义
- **不变量**：
  - 赋值目标必须是合法的 Python 标识符
  - 赋值内容必须是合法的 Python 表达式

## 📏 实体不变量规则

### PackageSpec 不变量
```gherkin
Given 一个 PackageSpec 实例
When 执行结构校验
Then
  - 包内的模块名称必须唯一
  - 子包名称必须唯一
  - 不得有循环嵌套的子包结构
```

```gherkin
Given 一个 PackageSpec 实例
When 执行合并操作
Then 相同路径的模块与子包必须执行递归合并
    且 合并结果必须保持包结构的完整性
```

### FunctionSpec 不变量
```gherkin
Given 一个 FunctionSpec 实例
When 执行参数校验
Then 参数顺序必须符合 Python 规范：
    1. 位置参数
    2. 带默认值的位置参数
    3. *args 可变参数
    4. 关键字-only 参数
    5. **kwargs 关键字可变参数
```

```gherkin
Given 一个实例方法的 FunctionSpec 实例
When 执行参数校验
Then 第一个参数必须是 self，且没有类型注解
```

```gherkin
Given 一个类方法的 FunctionSpec 实例
When 执行参数校验
Then 第一个参数必须是 cls，且没有类型注解
    且 必须包含 @classmethod 装饰器
```

### ClassSpec 不变量
```gherkin
Given 一个 ClassSpec 实例
When 添加方法
Then 方法名称在类内必须唯一
    且 __init__ 方法必须是实例方法
```

### TypeAnnotationSpec 不变量
```gherkin
Given 一个 TypeAnnotationSpec 实例
When 执行渲染
Then 必须生成合法的 Python 类型注解字符串
    且 所有引用的类型必须已经被正确导入
```

## 🎯 业务约束规则

### 代码生成约束
```gherkin
Given 任何代码生成请求
When 执行生成操作
Then
  - 生成的代码必须符合 Python 3.13 语法规范
  - 必须自动添加所有必要的导入语句
  - 生成的代码必须通过 black 格式化
  - 生成的代码必须通过 basedpyright 严格类型检查
  - 不得修改用户手动添加的、被标记为保留的代码片段
```

### 反向工程约束
```gherkin
Given 任何反向工程请求
When 执行解析操作
Then
  - 必须尽可能保留原始代码的业务语义
  - 无法识别的语法结构必须作为 RawCodeSpec 保留，不得丢失
  - 必须保留所有注释与文档字符串
  - 解析结果必须可以正向生成与原始代码等价的代码
```

### 命名约束
```gherkin
Given 任何代码元素的名称定义
When 进行合法性校验
Then
  - 模块/包名称：snake_case，全小写，下划线分隔
  - 类/异常名称：PascalCase，首字母大写
  - 函数/方法/变量/参数名称：snake_case，全小写，下划线分隔
  - 常量名称：UPPER_SNAKE_CASE，全大写，下划线分隔
```

## 🔒 访问约束
- 所有 AST 操作只能在本上下文内部执行，不得暴露给外部上下文
- 跨上下文访问只能使用不可变的 DTO 对象，不得直接传递 AST 节点引用
- 文件系统操作只能由本上下文的基础设施层执行
