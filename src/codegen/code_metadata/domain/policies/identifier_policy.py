from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


class IdentifierPolicy(ComponentPolicy):
    component_type: ClassVar[ComponentType] = ComponentType.IDENTIFIER
    dir_name: ClassVar[ComponentDir] = ComponentDir.IDENTIFIERS
    layer: ClassVar[ArchitectureLayer] = ArchitectureLayer.DOMAIN
