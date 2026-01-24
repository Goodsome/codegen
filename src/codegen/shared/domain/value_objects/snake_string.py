import caseconverter

from codegen.shared.domain.value_objects.naming_string import NamingString


class SnakeString(NamingString):
    def __new__(cls, value: str):
        if value.startswith("_"):
            return super().__new__(cls, value)
        converted = caseconverter.snakecase(value)
        return super().__new__(cls, converted)
