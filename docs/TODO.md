# 测试

* 制定一个测试代码风格标准
* 支持测试

# Feature

* 支持interfaces
* 支持bootstrap
  * 上下文中的container
* 支持entrypoints
* 增加tree get set的能力，不要再直接查询 codegen.yaml
  * reverse codegen.yaml 改动太大了。主要问题是codegen.yaml 没有规定的顺序
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