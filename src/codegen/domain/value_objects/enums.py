from enum import Enum


class ActionKind(str, Enum):
    use_case = "use_case"
    query = "query"
    
class CodeForm(str, Enum):
    single = "single"
    package = "package"