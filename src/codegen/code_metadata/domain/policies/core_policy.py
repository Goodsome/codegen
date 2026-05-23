from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


class CorePolicy(ComponentPolicy):
    component_type: ClassVar[ComponentType] = ComponentType.CORE
    dir_name: ClassVar[ComponentDir] = ComponentDir.CORE
    layer: ClassVar[ArchitectureLayer] = ArchitectureLayer.DOMAIN
