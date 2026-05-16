from dataclasses import dataclass

from codegen.code_metadata.application.dtos.generate_code_command import GenerateCodeCommand
from codegen.code_metadata.application.dtos.generate_code_result import GenerateCodeResult
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork


@dataclass
class GenerateCode:

    uow: UnitOfWork[ComponentRepository]
    generator: CodeGenerator
    
    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:
        c_id = ComponentId.reconstitute(cmd.component_id)
        with self.uow:
            component = self.uow.repository.get(c_id)
        code = self.generator.generate(component)
        return GenerateCodeResult(code=code)