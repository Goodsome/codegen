# Feature

* 增加tree get set的能力，不要再直接查询 codegen.yaml
  * set需要校验，并返回具体信息，而不是啥都往里面写
  * reverse codegen.yaml 改动太大了。主要问题是codegen.yaml 没有规定的顺序
* build 问题
  * enum
  * naming问题，比如：SOP
* 支持interfaces
* 支持bootstrap
  * 上下文中的container
* 支持entrypoints
* 代码清理工具

## 专属的 Bootstrap 目录（适合大型项目）
如果你的初始化逻辑很复杂（比如除了 DI 容器，还有日志配置、遥测 OpenTelemetry 设置、数据库连接池初始化等），可以单独开一个目录。
src/codegen
├── bootstrap/           <-- 【新增】启动引导层
│   ├── __init__.py
│   ├── container.py     <-- 定义 DI 容器
│   ├── config.py        <-- 加载配置
│   └── logging.py       <-- 配置日志
├── entrypoints/
├── domain_definition/
└── ...

## RENAME

什么时候你才真正需要记录“元数据”？
只有在一个极其特殊的痛点下，纯靠目录约定会失效：重命名（Renaming）追踪。
如果开发者在代码里把 CreateOrderUseCase 改成了 PlaceOrderUseCase，纯按名称匹配的逆向解析器可能会认为：旧的被删除了，同时新建了一个。它无法把修改前的 YAML 节点和修改后的代码关联起来。

即使未来要解决这个问题，更好的做法也不是在业务代码里写元数据，而是：

外置状态文件：类似 .codegen.lock 或 .codegen.state.json，在项目根目录维护一个文件 ID 到当前 AST 签名的映射字典（对业务代码零侵入）。

基于特征的启发式匹配：比较 AST 树的相似度（比如类里的方法没变，只是类名变了，判定为 Rename）。