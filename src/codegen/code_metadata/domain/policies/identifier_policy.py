from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


class IdentifierPolicy(ComponentPolicy):
    component_type: ClassVar[ComponentType] = ComponentType.IDENTIFIER
