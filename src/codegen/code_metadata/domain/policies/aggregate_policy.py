from dataclasses import dataclass
from typing import ClassVar

from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


@dataclass
class AggregatePolicy(ComponentPolicy):
    component_type: ClassVar[ComponentType] = ComponentType.AGGREGATE
