"""
Tree command - Display blueprint structure as a visual tree.
"""
from typing import Any, Optional

import typer
from rich.tree import Tree
from rich.console import Console
from pydantic import BaseModel
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)

# --- Configuration & Mappings ---

# 统一的 DDD 语义化图标库
# 设计原则：根据 DDD 概念的核心隐喻进行映射，同时兼容类名 (如 EntitySpec) 和字段名 (如 entities)
THEME_ICONS = {
    # --- 顶层与容器 ---
    "Blueprint": "📦", "Project": "📦",
    "contexts": "🧩", "BoundedContext": "🧩", "Context": "🧩",  # 🧩 拼图，代表系统由多个上下文拼接而成

    # --- 架构四大层 (Layers) ---
    "domain": "🏛️",           # 🏛️ 罗马柱/神庙，代表核心且不可动摇的业务基石
    "application": "⚙️",      # ⚙️ 齿轮，代表运转系统内部逻辑的引擎
    "infrastructure": "🏗️",   # 🏗️ 起重机/工地，代表底层的技术基础设施
    "interfaces": "🌐",       # 🌐 网络/地球，代表系统对外的网关和出入口

    # --- Domain 领域层元数据 ---
    "aggregates": "💠", "Aggregate": "💠", "AggregateSpec": "💠",    # 💠 核心枢纽，聚合根
    "entities": "🏷️", "Entity": "🏷️", "EntitySpec": "🏷️",             # 🏷️ 标签，隐喻 Entity 最核心的特征：“唯一标识 (Identity)”
    "value_objects": "💎", "ValueObject": "💎", "ValueObjectSpec": "💎", # 💎 钻石，代表不可变 (Immutable) 的值对象
    "enums": "🚥", "Enum": "🚥", "EnumSpec": "🚥",                   # 🚥 红绿灯，代表有限的、固定的状态流转
    "domain_events": "📣", "DomainEvent": "📣", "EventSpec": "📣",   # 📣 扩音器，代表向外广播的领域事件

    # --- Application 应用层 ---
    "use_cases": "🎯", "UseCase": "🎯", "UseCaseSpec": "🎯",         # 🎯 靶心，代表明确的业务用例和目标
    "ports": "🔌", "Port": "🔌", "PortSpec": "🔌",                   # 🔌 插头，端口和防腐层协议
    "services": "🛠️", "Service": "🛠️", "ServiceSpec": "🛠️",           # 🛠️ 组合工具，代表无状态的编排服务

    # --- Infrastructure 基础设施层 ---
    "implementations": "🧱", "Implementation": "🧱", "ImplementationSpec": "🧱", # 🧱 砖块，代表具体的落地实现代码

    # --- Interfaces 接口层 (新增) ---
    "InterfaceSpec": "🌐",
    "cli_commands": "⌨️", "CliCommand": "⌨️", "CliCommandSpec": "⌨️",      # ⌨️ 键盘，代表命令行输入
    "http_endpoints": "📡", "HttpEndpoint": "📡", "HttpEndpointSpec": "📡", # 📡 天线/雷达，代表接收外部 HTTP 请求
    "mcp_tools": "🤖", "McpTool": "🤖", "McpToolSpec": "🤖",                # 🤖 机器人，代表给 AI agent 使用的 MCP 工具

    # --- 默认后备 ---
    "default": "📄",
}

# --- Helper Functions ---

def get_icon(name: str) -> str:
    """
    统一获取图标。
    支持直接匹配，以及自动处理复数/Spec后缀的降级匹配。
    """
    # 1. 完美匹配 (例如直接查 "EntitySpec" 或 "entities")
    if name in THEME_ICONS:
        return THEME_ICONS[name]
    
    # 2. 去除 "Spec" 后缀查找 (如果查 "ConfigSpec" 没找到，试试 "Config")
    if name.endswith("Spec"):
        base_name = name[:-4]
        if base_name in THEME_ICONS:
            return THEME_ICONS[base_name]

    # 3. 尝试去除末尾的 "s" 查找单数 (如果查 "configs" 没找到，试试 "config")
    # 这对动态推断出来的小写字段名很有用
    if name.endswith("s"):
        singular = name[:-1]
        # 注意：这里可能需要首字母大写去匹配类名映射，比如 entities -> entity -> Entity
        if singular.capitalize() in THEME_ICONS:
            return THEME_ICONS[singular.capitalize()]

    return THEME_ICONS["default"]

def get_display_name(obj: Any) -> str:
    """Get display name from an object."""
    return getattr(obj, "name", obj.__class__.__name__)

def get_type_name(obj: Any) -> str:
    """Get type name from an object."""
    return obj.__class__.__name__

# --- Tree Building Logic ---

def _is_complex_node(model: BaseModel, ignore_fields: set[str]) -> bool:
    """
    智能探测：检查一个模型是否包含嵌套的子模型或子模型列表。
    如果包含，说明它是一个需要展开的分支；如果不包含，说明它是最底层的叶子节点。
    """
    # 兼容 Pydantic V2 (model_fields) 和 V1 (__fields__)
    fields = getattr(model, "model_fields", getattr(model, "__fields__", {}))
    
    for field_name in fields:
        if field_name in ignore_fields:
            continue
            
        value = getattr(model, field_name, None)
        
        # 如果包含嵌套单个模型
        if isinstance(value, BaseModel):
            return True
        # 如果包含模型列表
        if isinstance(value, (list, tuple, set)) and value:
            if isinstance(list(value)[0], BaseModel):
                return True
                
    return False

def add_model_children(model: BaseModel, tree: Tree) -> None:
    """
    全动态递归：通过反射 Pydantic 字段，自动推断并渲染层级结构。
    """
    fields = getattr(model, "model_fields", getattr(model, "__fields__", {}))
    
    # 约定：遇到这些基础属性字段，不需要将它们作为树节点渲染
    IGNORE_FIELDS = {"name", "description", "attributes", "behaviors", "inputs", "outputs", "dependencies", "operations", "members"}

    for field_name in fields:
        if field_name in IGNORE_FIELDS:
            continue

        value = getattr(model, field_name, None)
        if not value: # 忽略空列表或 None 的层级
            continue

        # --- 情况 1: 字段是一组元素的集合 (例如: cli_commands: list[CliCommandSpec]) ---
        if isinstance(value, (list, tuple, set)):
            items = list(value)
            # 确保列表里面装的是 Pydantic 模型
            if not items or not isinstance(items[0], BaseModel):
                continue
            
            section_icon = get_icon(field_name)
            icon_str = f"{section_icon} " if section_icon else ""
            section = tree.add(f"{icon_str}[bold]{field_name}[/bold] ({len(items)})")
            
            for item in items:
                item_name = get_display_name(item)
                item_icon = get_icon(get_type_name(item))
                
                # 动态探测：如果 item 内部还有结构，作为分支继续展开
                if _is_complex_node(item, IGNORE_FIELDS):
                    item_branch = section.add(f"{item_icon} [bold cyan]{item_name}[/bold cyan]")
                    add_model_children(item, item_branch)
                # 如果内部没有子结构了，就是叶子节点
                else:
                    section.add(f"{item_icon} [bold cyan]{item_name}[/bold cyan]")

        # --- 情况 2: 字段是单一配置模块 (例如: interfaces: InterfaceSpec, domain: DomainSpec) ---
        elif isinstance(value, BaseModel):
            # 只有当这个模块内部真的包含其他子结构时，我们才为它建立一个新的层级树枝
            if _is_complex_node(value, IGNORE_FIELDS):
                section_icon = get_icon(field_name)
                icon_str = f"{section_icon} " if section_icon else ""
                layer_tree = tree.add(f"{icon_str}[bold]{field_name}[/bold]")
                
                # 递归进入下一层
                add_model_children(value, layer_tree)

# --- Command Entry Point ---

@inject
def _load_blueprint(
    cmd: LoadBlueprintCommand,
    use_case: LoadBlueprint = Provide["domain_definition_container.load_blueprint"],
) -> Optional[Any]:
    return use_case.execute(cmd)

def tree() -> None:
    """
    Tree: Display blueprint structure as a visual tree.

    Provides a hierarchical overview of your project's DDD structure,
    making it easy to understand the organization of contexts,
    aggregates, entities, and other components.

    Example:
        $ codegen tree
    """
    console = Console()

    try:
        result = _load_blueprint(LoadBlueprintCommand())

        # Safe fallback if result object is structured differently
        blueprint = getattr(result, "blueprint", None) if result else None
        
        if not blueprint:
            console.print("[red]Error: Blueprint not found or failed to load.[/red]")
            raise typer.Exit(1)

        root = Tree(f"📦 [bold]Project: {get_display_name(blueprint)}[/bold]")
        add_model_children(blueprint, root)

        console.print(root)

    except KeyError as e:
        console.print(f"[red]Error: Configuration or Dependency missing - {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        # Consider logging the stack trace here if running in debug mode
        console.print(f"[red]Error building tree: {e}[/red]")
        raise typer.Exit(1)