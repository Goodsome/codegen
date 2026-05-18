from pathlib import Path
from typing import ClassVar, override
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.execptions.external_component_not_support import ExternalComponentNotSupport
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


class ExternalPolicy(ComponentPolicy):

    component_type: ClassVar[ComponentType] = ComponentType.EXTERNAL

    @property
    @override
    def target_path(self) -> Path:
        raise ExternalComponentNotSupport("traget_path")
    
    @override
    def get_import_module(self, context: str, component_name: str) -> str:
        return f"{context}"