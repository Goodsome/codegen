from abc import ABC, abstractmethod

from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec


class SourceCodePort(ABC):
    """Port for bidirectional translation between Spec objects and Python source code."""

    @abstractmethod
    def render_module(
        self, module_spec: ModuleSpec, imports: list[ImportFromSpec]
    ) -> str: ...

    @abstractmethod
    def parse_module(
        self,
        source_code: str,
        module_name: str,
    ) -> ModuleSpec: ...
