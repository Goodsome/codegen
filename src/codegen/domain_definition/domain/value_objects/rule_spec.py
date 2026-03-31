from codegen.shared.models import ValueObject
from codegen.shared.domain.value_objects.pascal_string import PascalString


class RuleSpec(ValueObject):
    """BDD rule specification with given/when/then"""

    name: PascalString
    given: str
    when: str
    then: str
