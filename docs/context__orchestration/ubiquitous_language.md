---
name: Orchestration 通用语言与规约
description: Orchestration 上下文内的名词解释、实体不变量与业务约束
type: project
---

# 📖 Orchestration 通用语言与规约

## 🔤 核心名词解释

### 1. BuildResult (构建结果)
- **定义**：代码生成操作的顶级返回结果对象
- **业务含义**：聚合了整个构建过程的所有信息，包括状态、文件结果、统计信息、消息等
- **不变量**：
  - 必须包含明确的构建状态（SUCCESS/FAILURE/WARNING）
  - 必须包含所有生成文件的详细结果
  - 必须包含完整的构建统计信息

### 2. FileResult (文件结果)
- **定义**：单个文件生成操作的结果对象
- **业务含义**：描述单个文件的生成状态、路径、消息、差异等信息
- **不变量**：
  - 必须包含明确的文件状态（CREATED/UPDATED/SKIPPED/FAILED）
  - 必须包含文件的完整路径
  - 失败状态必须包含详细的错误信息

### 3. BuildStats (构建统计)
- **定义**：构建操作的聚合统计信息对象
- **业务含义**：统计构建过程中各种状态的文件数量、执行时长等信息
- **不变量**：
  - 所有计数必须非负
  - 总文件数等于各状态文件数之和
  - 执行时长必须非负

### 4. BuildStatus (构建状态枚举)
- **定义**：构建操作的整体状态枚举
- **业务含义**：标识整个构建操作的最终状态
- 枚举值：
  - SUCCESS：构建完全成功，所有文件都生成成功
  - FAILURE：构建失败，至少有一个文件生成失败
  - WARNING：构建成功，但有警告信息

### 5. FileStatus (文件状态枚举)
- **定义**：单个文件生成操作的状态枚举
- **业务含义**：标识单个文件的生成结果状态
- 枚举值：
  - CREATED：新创建的文件
  - UPDATED：内容有更新的已存在文件
  - SKIPPED：无需更新的文件
  - FAILED：生成失败的文件

## 📏 实体不变量规则

### BuildResult 不变量
```gherkin
Given 一个 BuildResult 实例
When 执行状态校验
Then
  - 如果任何 FileResult 的状态是 FAILED，整体状态必须是 FAILURE
  - 如果没有 FAILED 但有 WARNING 消息，整体状态必须是 WARNING
  - 如果没有 FAILED 也没有 WARNING 消息，整体状态必须是 SUCCESS
```

```gherkin
Given 一个 BuildResult 实例
When 执行统计校验
Then BuildStats 中的统计数据必须与 FileResult 列表中的实际数据一致
    且 total_files = created_count + updated_count + skipped_count + failed_count
```

### FileResult 不变量
```gherkin
Given 一个 FileResult 实例
When 状态是 FAILED
Then 必须包含非空的错误消息
```

```gherkin
Given 一个 FileResult 实例
When 状态是 UPDATED
Then 必须包含非空的 diff 信息，展示新旧内容的差异
```

### BuildStats 不变量
```gherkin
Given 一个 BuildStats 实例
When 执行统计校验
Then
  - total_files >= 0
  - created_count >= 0
  - updated_count >= 0
  - skipped_count >= 0
  - failed_count >= 0
  - duration_ms >= 0
```

## 🎯 业务约束规则

### CLI 命令约束
```gherkin
Given 任何 CLI 命令请求
When 执行处理
Then
  - 必须提供友好的帮助信息与参数提示
  - 必须支持 --help 参数查看命令用法
  - 错误信息必须清晰易懂，包含问题原因与解决方案
  - 执行过程中必须提供实时进度反馈
```

### MCP 工具约束
```gherkin
Given 任何 MCP 工具请求
When 执行处理
Then
  - 必须遵循 MCP 协议规范
  - 参数必须有明确的类型定义与校验
  - 响应必须遵循统一的格式规范
  - 错误信息必须包含明确的错误码与描述
```

### 跨上下文调用约束
```gherkin
Given 任何跨上下文调用请求
When 执行调用
Then
  - 必须通过应用服务接口调用，不得直接访问其他上下文的领域层
  - 所有参数与返回值必须使用不可变的 DTO 对象
  - 必须处理所有可能的异常情况，返回统一的错误格式
  - 调用超时必须有明确的处理机制
```

## 🔒 访问约束
- 所有外部请求必须经过本上下文入口，不得直接访问 DomainDefinition 或 PythonGen 上下文
- 本上下文内部的流程编排逻辑不得暴露给外部
- 所有对外接口必须提供明确的版本控制与兼容性保证
