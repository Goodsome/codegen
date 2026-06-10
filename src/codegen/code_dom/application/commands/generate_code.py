from dataclasses import dataclass
from pydantic import BaseModel

from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.ports.code_generator import CodeGenerator
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class GenerateCodeCommand(BaseModel):
    code_documents: list[CodeDocument]


@dataclass
class GenerateCodeHandler:
    code_generator: CodeGenerator
    file_system: FileSystemPort

    def execute(self, cmd: GenerateCodeCommand):
        
        for code_document in cmd.code_documents:
            print(f"will write code to {self.file_system.root}/{code_document.physical_path}")
            # code = self.code_generator.generate(code_document)
            # self.file_system.write_file(
                # path=code_document.physical_path,
                # content=code
            # )