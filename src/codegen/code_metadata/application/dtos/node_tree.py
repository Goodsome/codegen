from dataclasses import dataclass, field

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto


@dataclass
class NodeTree:
    """目录树节点：递归结构，每个节点持有 CodeNodeDto 及其子树。"""

    node: CodeNodeDto
    children: list["NodeTree"] = field(default_factory=list)
