from abc import ABC, abstractmethod

from codegen.code_metadata.application.dtos.code_node_dto import ModuleNodeDto
from codegen.code_metadata.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.application.registry.node_registry import NodeRegistry


class FileDiffer(ABC):
    @abstractmethod
    def get_diff_metric(
        self, module: ModuleNodeDto, node_registry: NodeRegistry
    ) -> FileMetrics: ...
