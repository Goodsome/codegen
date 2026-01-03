import black

from codegen.python_gen.domain.ports.code_formatter import CodeFormatter


class BlackCodeFormatter(CodeFormatter):

    def format_code(self, code: str) -> str:
        return black.format_str(code, mode=black.Mode())
