from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.enums import GherkinKeyword


class GherkinStep(ValueObject):
    """Gherkin 场景中的单一步骤，由关键字和步骤文本组成。"""

    keyword: GherkinKeyword
    text: str
