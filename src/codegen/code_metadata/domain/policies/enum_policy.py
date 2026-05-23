from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


class EnumPolicy(ComponentPolicy):
    component_type: ClassVar[ComponentType] = ComponentType.ENUM
    dir_name: ClassVar[ComponentDir] = ComponentDir.ENUMS
    layer: ClassVar[ArchitectureLayer] = ArchitectureLayer.DOMAIN
    
